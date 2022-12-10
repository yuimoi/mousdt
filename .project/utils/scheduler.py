import datetime
import time
from flask import current_app
import config
from create_app import create_app
from exts import cache
from exts import db
from exts import scheduler
from models import OrderModel, TransferModel, WalletModel
from utils.function import clean_pending_order, clean_locked_wallet, order_paid_amount, get_api, get_config


def start_scheduler():
    # 检查超时订单，检查超时锁定钱包，检查最新交易
    if not scheduler.get_job('check job'):
        scheduler.add_job(check_job_with_context, 'interval', seconds=config.wallet_listener_interval, id="check_job")

    if not scheduler.get_job('clean_job'):
        start_date = datetime.datetime.now() + datetime.timedelta(seconds=int(config.wallet_listener_interval / 2))  # 报PytzUsageWarning
        scheduler.add_job(clean_job_with_context, 'interval', start_date=start_date,
                          seconds=config.wallet_listener_interval, id="clean_job")


def check_job_with_context():
    context_app = create_app()
    with context_app.app_context():
        try:
            check_job()
        except Exception as e:
            current_app.logger.exception(e)


def clean_job_with_context():
    context_app = create_app()
    with context_app.app_context():
        try:
            clean_job()
        except Exception as e:
            current_app.logger.exception(e)


def check_job():
    current_app.logger.debug('check_job')

    result = OrderModel.query.filter(OrderModel.status == 0).first()
    if not result:
        # 没有待支付订单则清除值，等待下一次开始订单
        cache.set('end_block_timestamp', None)
        return None

    # 第一次执行开始时间为当前时间减去两倍定时间隔，结束时间为当前时间减去一倍定时间隔，以订单最后一个间隔时间的漏单代价弥补服务器本地时间的误差
    # 非第一次执行开始时间为上一次的结束时间，结束时间为当前时间减去一倍定时间隔，可以忽略代码运行带来的误差，还可以将之前定时器执行网络错误的时间段在这一次一起进行
    # API漏单可能性：1.交易发生在最后一次API的时间段内，并且API执行时出错 2.交易发生在订单结束前一个间隔时间内
    start_block_timestamp = cache.get('end_block_timestamp')
    if not start_block_timestamp:
        start_block_timestamp = int((time.time() - config.wallet_listener_interval * 2) * 1000)
    else:
        start_block_timestamp = int(cache.get('end_block_timestamp'))
    end_block_timestamp = int((time.time() - config.wallet_listener_interval) * 1000)

    # 程序启动后，存在未完成订单，且api成功执行过一次，且之后api失效过久的时候，会导致查询时间范围过大，往前追溯最多2分钟
    if end_block_timestamp - start_block_timestamp > 120 * 1000:
        start_block_timestamp = int((end_block_timestamp - 60) * 1000)

    result = db.session.query(OrderModel.network).group_by(OrderModel.network).all()
    network_list = [temp[0] for temp in result]

    transfer_list = []
    for network in network_list:
        if network == 'tron':
            get_transfer_list_by_time_range = get_api(network).get_transfer_list_by_time_range

            current_app.logger.debug(f'query {network} api [{datetime.datetime.fromtimestamp(int(start_block_timestamp / 1000)).strftime("%m-%d %H:%M:%S")} - {datetime.datetime.fromtimestamp(int(end_block_timestamp / 1000)).strftime("%m-%d %H:%M:%S")}]')
            transfer_list = get_transfer_list_by_time_range(start_block_timestamp=start_block_timestamp,end_block_timestamp=end_block_timestamp)
            # transfer_list = get_transfer_list_by_time_range(start_block_timestamp=1668788327000, end_block_timestamp=1668788329000)

    cache.set('end_block_timestamp', end_block_timestamp)

    if not transfer_list:
        return None

    # 对比数据库是否有对应的钱包地址
    address_list = [temp.to_address for temp in transfer_list]

    # 一次性执行太多会报错
    wallet_to_update_list = []
    chunk_size = 500
    for i in range(0, len(address_list), chunk_size):
        chunk = address_list[i:i + chunk_size]
        wallet_to_update_list_temp = WalletModel.query.filter(WalletModel.address.in_(chunk)).all()
        wallet_to_update_list += wallet_to_update_list_temp

    if not wallet_to_update_list:
        return None

    # 找出待更新的钱包和对应的交易和对应的订单
    wallet_transfer_list = []
    for wallet in wallet_to_update_list:
        for transfer in transfer_list:
            if transfer.to_address == wallet.address:
                wallet_transfer_list.append({'wallet': wallet, 'transfer': transfer})

    # 添加交易到数据库,因为API的查询时间的问题可能会取到重复的交易记录，如果交易存在则从wallet_transfer_list删除
    for i in wallet_transfer_list[:]:
        result = TransferModel.query.filter(TransferModel.transaction_id == i['transfer'].transaction_id).first()
        if result:
            wallet_transfer_list.remove(i)
        else:
            db.session.add(i['transfer'])
            db.session.commit()

    # 找出相应的钱包、交易、订单，其中订单可能为空
    wallet_transfer_order_list = []
    for i in wallet_transfer_list:
        wallet = i['wallet']
        transfer = i['transfer']
        order = OrderModel.query.filter(
            (OrderModel.status == 0) &
            (OrderModel.wallet_id == wallet.id)
        ).first()
        wallet_transfer_order_list.append({'wallet': wallet, 'transfer': transfer, 'order': order})

    # 更新交易，将交易绑定到订单上，并找到对应订单的对应的钱包，并将余额加上
    for i in wallet_transfer_order_list:
        if i['order']:
            order = i['order']
            transfer = i['transfer']
            transfer.order = order

            order.paid_price += transfer.price
            order.wallet.balance += transfer.price
            db.session.commit()

    # 统计订单的金额，在时间范围内的交易
    # 若够数了，则订单完成，解锁钱包，更新订单，发送回调
    for i in wallet_transfer_order_list:
        if not i['order']:
            continue
        order = i['order']
        wallet = i['wallet']
        # result = TransferModel.query.filter( TransferModel.order == order).all()
        #
        # receive_amount = 0
        # for transfer in result:
        #     receive_amount += transfer.quant / 1e6
        receive_amount = order_paid_amount(order.id)

        # 由于是浮点数，为保险起见等于符号采用容差判断
        epsilon = 0.00005
        if abs(receive_amount - order.price) < epsilon or receive_amount > order.price:
            # 更新订单
            order.status = 1

            # 解锁钱包
            wallet.status = 1
            wallet.start_lock_time = None
            wallet.end_lock_time = None
            db.session.commit()

            # 发送回调
            order.notify()


# 订单超时，订单完成都会触发这个函数
def clean_job():
    current_app.logger.debug('clean job')
    # 标记超时订单,解锁钱包

    clean_pending_order()
    clean_locked_wallet()
