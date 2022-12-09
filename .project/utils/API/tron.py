import json
import requests
from flask import current_app
from models import TransferModel, WalletModel
from exts import db
from utils.function import hex_to_base58, get_config, tron_address_to_parameter
import base58

from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.providers import HTTPProvider


headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}

tron_usdt_contracts = r"TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"


# 该函数递归调用，直至翻到最后一页，如果超过五页则修改时间范围调用自己，每一次递归都把下一层的transfer_list传到上一层
def get_transfer_list_by_time_range(**kwargs):
    headers['tron-PRO-API-KEY'] = get_config('trongrid_key')
    # timestamp只能用整数，单位是毫秒
    url = f"https://api.trongrid.io/v1/contracts/{tron_usdt_contracts}/events?event_name=Transfer&only_unconfirmed=false&only_confirmed=false&limit=200&order_by=block_timestamp%2Casc"

    start_block_timestamp = kwargs.get("start_block_timestamp", None)
    end_block_timestamp = kwargs.get("end_block_timestamp", None)
    if start_block_timestamp and end_block_timestamp:
        url = url + f"&min_block_timestamp={start_block_timestamp}&max_block_timestamp={end_block_timestamp}"

    current_app.logger.debug(f'get url:{url}')
    response = requests.get(url, headers=headers, timeout=5)

    if response.status_code != 200:
        raise Exception(f"status code:{response.status_code} url:{url}")

    data_list = json.loads(response.text)['data']

    if json.loads(response.text)['meta'].get("links"):
        next_link = json.loads(response.text)['meta']['links']['next']
    else:
        next_link = None

    transfer_list = []
    # 这里的next_link相当于翻页，使用指纹作为页数，当查询的事件数量超过第1000个的时候，则会报错，不会返回内容
    if next_link:
        page_num = 1
        while next_link:
            page_num += 1
            if page_num > 5:
                # 获取第5页最后一个交易的时间戳，作为开始时间戳，结束时间戳不变，再次调用自己生成新的查询
                start_block_timestamp = data_list[-1]['block_timestamp']
                transfer_list = transfer_list + get_transfer_list_by_time_range(start_block_timestamp=start_block_timestamp,
                                                               end_block_timestamp=end_block_timestamp)
                break

            current_app.logger.debug(f'get url:{next_link}')
            response = requests.get(next_link, headers=headers, timeout=5)
            data_list = data_list + json.loads(response.text)['data']
            if json.loads(response.text)['meta'].get("links"):
                next_link = json.loads(response.text)['meta']['links']['next']
            else:
                next_link = None

    for data in data_list:
        transfer = TransferModel()
        transfer.price = int(data['result']['value']) / 1e6
        transfer.transaction_id = data['transaction_id']

        transfer.create_time = int(data['block_timestamp'] / 1000.0)

        transfer.from_address = hex_to_base58(data['result']['from'])
        transfer.to_address = hex_to_base58(data['result']['to'])
        transfer.currency = "USDT"
        transfer.network = "tron"

        # 跳过0元攻击
        if int(data['result']['value']) == 0:
            continue

        transfer_list.append(transfer)

    # 去除重复交易
    seen_transaction_id = set()
    new_list = []
    for transfer in transfer_list:
        if transfer.transaction_id not in seen_transaction_id:
            new_list.append(transfer)
            seen_transaction_id.add(transfer.transaction_id)
    transfer_list = new_list

    return transfer_list


def is_work(network):
    if network == "tron":
        try:
            result = get_transfer_list_by_time_range(start_block_timestamp=1670038526000, end_block_timestamp=1670038528000)
        except:
            return False

        if len(result):
            return True

    return False


def get_balance(address):
    url = 'https://api.trongrid.io/wallet/triggerconstantcontract'
    payload = {
        'owner_address': base58.b58decode_check(address).hex(),
        'contract_address': base58.b58decode_check(tron_usdt_contracts).hex(),
        'function_selector': 'balanceOf(address)',
        'parameter': tron_address_to_parameter(address),
    }
    headers['tron-PRO-API-KEY'] = get_config('trongrid_key')
    current_app.logger.debug(f'post url:{url}')
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if response.status_code == 401:
        raise Exception(f"API密钥错误")

    if response.status_code != 200:
        raise Exception(f"request error code:{response.status_code} url:{url}")

    val = data['constant_result'][0]
    balance = int(val, 16) / 1e6

    return balance


def get_fee_balance(address):
    url = "https://api.trongrid.io/walletsolidity/getaccount"
    payload = {
        "address": address,
        "visible": True
    }

    headers['tron-PRO-API-KEY'] = get_config('trongrid_key')
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()
    if response.status_code == 401:
        raise Exception(f"API密钥错误")

    if response.status_code != 200:
        raise Exception(f"错误代码:{response.status_code} 请求网址:{url}")

    if data:
        trx_balance = data['balance'] / 1e6
    else:
        trx_balance = 0

    return trx_balance


def transfer_fee(from_address, to_address, price, pkey):
    client = Tron(HTTPProvider(api_key=get_config('trongrid_key')))
    priv_key = PrivateKey(bytes.fromhex(pkey))
    amount = int(price * 1e6)

    txn = (
        client.trx.transfer(from_address, to_address, amount)
            .build()
            .sign(priv_key)
    )

    current_app.logger.debug(f'广播交易：从地址 {from_address} 向地址 {to_address} 转账 {price} trx')

    result = txn.broadcast().wait()

    current_app.logger.debug(f'交易结果：{result}')

    transfer = TransferModel()
    transfer.currency = 'trx'
    transfer.network = 'tron'
    transfer.transaction_id = result['id']
    transfer.price = price
    transfer.create_time = int(result['blockTimeStamp'] / 1000)
    transfer.from_address = from_address
    transfer.to_address = to_address
    transfer.message = f"成功"
    transfer.purpose = 'fee'

    db.session.add(transfer)
    db.session.commit()

    return True


def transfer(from_address, to_address, price, pkey, currency="USDT"):
    # get_contract()调用一次API, build()调用两次API，第一次获取当前区块，第二次获取权限列表
    client = Tron(HTTPProvider(api_key=get_config('trongrid_key')))
    priv_key = PrivateKey(bytes.fromhex(pkey))
    amount = int(price * 1e6)

    if currency == 'USDT':
        contract_address = r"TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    else:
        raise Exception(f'Not support currency:{currency}')

    contract = client.get_contract(contract_address)

    txn = (
        contract.functions.transfer(to_address, amount)
            .with_owner(from_address)  # address of the private key
            .fee_limit(20_000_000)
            .build()
            .sign(priv_key)
    )
    current_app.logger.debug(f'广播交易：从地址 {from_address} 向地址 {to_address} 转账 {price} {currency}')

    result = txn.broadcast().wait()

    current_app.logger.debug(f'交易结果：{result}')

    fee = result.get('fee') / 1e6 if result.get('fee') else 0

    if result['receipt']['result'] == 'SUCCESS':
        success_fail_msg = '成功'
        fail_msg = ''

        # 刷新钱包
        for address in [from_address, to_address]:
            WalletModel.query.filter(WalletModel.address == address).update({'balance': get_balance(address), 'fee_balance': get_fee_balance(address)})
        db.session.commit()

    else:
        success_fail_msg = '失败'
        fail_msg = result['resMessage']

    transfer = TransferModel()
    transfer.currency = currency
    transfer.network = 'tron'
    transfer.transaction_id = result['id']
    transfer.price = price
    transfer.create_time = int(result['blockTimeStamp'] / 1000)
    transfer.from_address = from_address
    transfer.to_address = to_address
    transfer.message = f"{success_fail_msg}，消耗手续费{fee}，消息：{fail_msg}"
    transfer.purpose = 'transfer'

    db.session.add(transfer)
    db.session.commit()

    if result['receipt']['result'] == 'SUCCESS':
        # 成功
        return True
    else:
        # 失败
        return False
