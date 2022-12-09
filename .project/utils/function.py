import time

import base58
from cryptography.fernet import Fernet
from flask import g

from exts import db
from models import OrderModel, WalletModel, TransferModel, ConfigModel


def get_config(config_key: str):
    # 同一个context只查一次数据库
    if not g.get('config'):
        global_config = ConfigModel.get_all()
        g.config = global_config

    return g.config.get(config_key, None)


def get_api(network):
    api = getattr(__import__('utils.API', fromlist=[network]), network)
    return api


def free_wallet(network='tron'):
    result = WalletModel.query.filter(WalletModel.status == 1, WalletModel.network == network).order_by(
        *WalletModel.query_order()).first()
    return result


def clean_pending_order():
    # 标记超时订单
    # 注意这里，虽然订单创建在定时任务之前，但是由于时间精度问题，订单时间精度高，要加一秒增量
    OrderModel.query.filter((OrderModel.status == 0) & (OrderModel.end_time <= int(time.time()))).update({"status": -1})

    db.session.commit()


def clean_locked_wallet():
    # 标记超时钱包锁定
    WalletModel.query.filter((WalletModel.status == 0) & (WalletModel.end_lock_time <= time.time())).update(
        {'status': 1, 'end_lock_time': None, 'start_lock_time': None})
    db.session.commit()


def order_paid_amount(order_id):
    result = TransferModel.query.filter(TransferModel.order_id == order_id).all()

    receive_amount = 0
    for transfer in result:
        receive_amount += transfer.price
    return receive_amount


def encrypt(message: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(message)


def decrypt(token: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(token)


def generate_encrypt_key():
    return Fernet.generate_key()


def hex_to_base58(hex_string):
    if hex_string[:2] in ["0x", "0X"]:
        hex_string = "41" + hex_string[2:]
    bytes_str = bytes.fromhex(hex_string)
    base58_str = base58.b58encode_check(bytes_str)
    return base58_str.decode("UTF-8")


def base58_to_hex(base58_string):
    asc_string = base58.b58decode_check(base58_string)
    return asc_string.hex().upper()


def bordered_text(text):
    lines = text.splitlines()
    width = max(len(s) for s in lines)
    res = ['┌' + '─' * width + '┐']
    for s in lines:
        res.append('│' + (s + ' ' * width)[:width] + '│')
    res.append('└' + '─' * width + '┘')
    return '\n'.join(res)


def tron_address_to_parameter(addr):
    return "0" * 24 + base58.b58decode_check(addr)[1:].hex()


def refresh_wallet(wallet, force_refresh=False):
    if not force_refresh:
        if wallet.refresh_time and wallet.refresh_time + int(get_config('wallet_refresh_cooldown_time')) > int(
                time.time()):
            return wallet

    network = wallet.network
    api = get_api(network)

    balance = api.get_balance(wallet.address)
    fee_balance = api.get_fee_balance(wallet.address)
    wallet.balance = balance
    wallet.fee_balance = fee_balance
    wallet.refresh_time = int(time.time())
    db.session.commit()
    return wallet


