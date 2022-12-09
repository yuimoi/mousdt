import config
from create_app import create_app
from flask_sqlalchemy import inspect
from models import ConfigModel,AdminModel
import random
import string
from utils.function import bordered_text, generate_encrypt_key
from utils.tool.generate_wallet import generate_wallet
from exts import db, cache, scheduler, log_handler
import ntplib


def first_run(app):
    ntp_client = ntplib.NTPClient()
    ntp_server_list = ['cn.pool.ntp.org', 'hk.pool.ntp.org', 'us.pool.ntp.org']
    response = None

    for ntp_server in ntp_server_list:
        retry_threshold = 3
        retry_times = 0

        for _ in range(retry_threshold):
            try:
                response = ntp_client.request(ntp_server, version=3, timeout=2)
                break
            except:
                retry_times += 1
        if response:
            break

    if not response:
        raise Exception(f'从[{",".join(ntp_server_list)}]获取时间失败')

    time_offset = -response.offset
    if time_offset >= 0 and time_offset > config.wallet_listener_interval:
        raise Exception(f"Your system time is faster {time_offset} seconds, please sync time")

    if time_offset < 0 and -time_offset > config.wallet_listener_interval * 2:
        raise Exception(f"Your system time is slower {-time_offset} seconds, please sync time")

    # 创建默认表，写入默认数据
    context_app = create_app()

    with context_app.app_context():
        inspector = inspect(db.engine)

        if not inspector.has_table("config"):
            db.create_all()
            db.session.commit()

            epay_merchant_key = ''.join(random.choice(string.ascii_lowercase) for _ in range(16))
            db.session.add(ConfigModel(key='epay_merchant_key', value=epay_merchant_key, name='易支付商户密钥'))
            db.session.add(ConfigModel(key='order_duration', value='900',name='订单持续时间'))
            db.session.add(ConfigModel(key='wallet_refresh_cooldown_time', value='100',name='钱包刷新冷却时间'))
            db.session.add(ConfigModel(key='encrypt_key', value=generate_encrypt_key().decode(),name='加密密钥'))
            db.session.add(ConfigModel(key='trongrid_key', value='',name='trongrid API 密钥'))
            db.session.add(ConfigModel(key='transfer_trx_min', value='20',name='trx最小值（手续费低于该值从手续费钱包补到最大值）'))
            db.session.add(ConfigModel(key='transfer_trx_max', value='40',name='trx最大值'))

            admin_password = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
            db.session.add(AdminModel(username='admin', password=admin_password))

            print(bordered_text(f'  Login Info\nusername:admin\npassword:{admin_password}\nepay_merchant_key:{epay_merchant_key}\n\n!!!This message is only shown once!!!'))
            db.session.commit()

            # 第一次运行时自动创建钱包
            # generate_wallet()

    cache.set('end_block_timestamp', None)

    # # 不应写在create_app，当create_app被调用一次就会新创建一个log实例，导致出现重复日志
    app.logger.addHandler(log_handler())

    # 创建定时任务
    from utils.scheduler import start_scheduler
    start_scheduler()
    scheduler.start()

    return app
