import collections
import hashlib
import os
import random
import time
import urllib.parse

import requests
from flask import Blueprint
from flask import request, redirect, current_app, url_for

from models import OrderModel
from pay import bp as master_bp
from utils import restful
from utils.function import get_config, encrypt, get_api

# 接口的唯一标识符，用于路径
identify_name = os.path.basename(__file__).replace('.py', '')
# 接口的中文名，用于展示
name = '易支付'

SDK_bp = Blueprint(identify_name, __name__, url_prefix=f'/{identify_name}')
master_bp.register_blueprint(SDK_bp)


@SDK_bp.route('/submit.php', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        request_data = request.json
    elif request.method == 'GET':
        request_data = request.args
    else:
        return "request method err"

    # # 简单HTML注入检查
    # for temp in request_data:
    #     if "<" in request_data[temp] or ">" in request_data[temp]:
    #         return restful.params_err(message='input invalid')

    order_submit_data = {}
    order_submit_data['pid'] = request_data.get('pid')
    order_submit_data['type'] = request_data.get('type')
    order_submit_data['out_trade_no'] = request_data.get('out_trade_no')
    order_submit_data['notify_url'] = request_data.get('notify_url')  # 支付成功后的回调通知地址
    order_submit_data['return_url'] = request_data.get('return_url')  # 支付成功后的跳转地址
    order_submit_data['name'] = request_data.get('name')
    order_submit_data['money'] = request_data.get('money')
    order_submit_data['sign'] = request_data.get('sign')
    order_submit_data['sign_type'] = request_data.get('sign_type')
    order_submit_data['sitename'] = request_data.get('sitename')
    order_submit_data['param'] = request_data.get('param')

    # 支付方式
    if order_submit_data['type'] == 'tron':
        network = 'tron'
    else:
        network = 'tron'
        # return restful.params_err('no such type')

    if order_submit_data['sign_type'] != "MD5":
        return restful.params_err(message='sign type err')

    try:
        int(order_submit_data['money'])
    except:
        return restful.params_err(message='only integer price')

    if request_data.get('pid') is None or request_data.get('type') is None or request_data.get('out_trade_no') is None \
            or request_data.get('notify_url') is None or request_data.get('notify_url') is None or request_data.get(
        'return_url') is None \
            or request_data.get('name') is None or request_data.get('money') is None or request_data.get(
        'sign') is None or request_data.get('sign_type') is None:
        return restful.params_err(message='para miss')

    # 签名校验
    sign_real = epay_sign(order_submit_data)

    if order_submit_data['sign'].lower() != sign_real.lower():
        return restful.params_err(message='sign fail')

    is_work = get_api(network).is_work

    if not is_work(network):
        return restful.params_err(message='API not work')

    # 创建订单
    order = OrderModel()
    order.notify_type = identify_name
    order.network = network
    order.merchant_id = order_submit_data['pid']  # 商户id
    order.merchant_order_id = order_submit_data['out_trade_no']  # 商户订单id
    order.notify_url = order_submit_data['notify_url']  # 回调地址
    order.return_url = order_submit_data['return_url']  # 支付成功返回地址
    order.merchant_good_name = order_submit_data['name']  # 商户商品名
    order.price = order_submit_data['money']  # 金额
    order.create_time = int(time.time())
    order.end_time = order.create_time + int(get_config('order_duration'))
    order = order.create()

    if not order:
        return restful.params_err(message='no free wallet')

    token = encrypt(str(order.id).encode(), get_config('encrypt_key')).decode()

    # 跳转支付页面
    return redirect(f"/page/pay/index.html?token={token}")


def notify(order: OrderModel):
    notify_url = order.notify_url
    notify_data = {}
    notify_data['pid'] = order.merchant_id
    notify_data['trade_no'] = order.id
    notify_data['out_trade_no'] = order.merchant_order_id
    notify_data['type'] = order.currency
    notify_data['name'] = order.merchant_good_name
    notify_data['money'] = order.price
    notify_data['trade_status'] = "TRADE_SUCCESS"
    # notify_data['param'] = None
    notify_data['sign_type'] = "MD5"
    notify_data['sign'] = epay_sign(notify_data)

    current_app.logger.debug(f"发送回调: url:{notify_url}, data:{notify_data}")

    # 回调的headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
    }

    try:
        requests.get(notify_url, params=notify_data, headers=headers)
    except:
        if "https" in notify_url:
            notify_url = notify_url.replace("https", "http")
            requests.get(notify_url, params=notify_data, headers=headers)


def generate_order_url(**kwargs):
    data = {}
    data['pid'] = kwargs.get("pid", 1)
    data['type'] = kwargs.get("", 'tron')
    data['notify_url'] = 'notify_url'
    data['return_url'] = 'return_url'
    data['out_trade_no'] = int(random.random() * 10e10)
    data['name'] = 'test'
    data['money'] = kwargs.get("price", 1)
    data['sitename'] = ''
    data = dict(collections.OrderedDict(sorted(data.items())))

    sign = ''

    for i in data:
        if data[i] == '' or i == 'sign':
            continue
        if sign != '':
            sign += '&'

        sign += f"{i}={data[i]}"
    epay_merchant_key = get_config('epay_merchant_key')
    # epay_merchant_key = "diitapzgbrbbyfis"
    sign = hashlib.md5((sign + epay_merchant_key).encode('utf-8')).hexdigest()
    data['sign'] = sign
    data['sign_type'] = 'MD5'
    submit_url = url_for(f"pay.{identify_name}.submit")
    return submit_url + "?" + "&".join(
        [f"{temp}=" + urllib.parse.quote(str(data[temp]), safe="") for temp in data if data[temp]])


def epay_sign(data):
    # 签名校验
    # 删除sign sign_type 空值
    sign_data = {}
    for dic_key in data.keys():
        if dic_key != 'sign' and dic_key != 'sign_type' and data[dic_key] is not None:
            sign_data[dic_key] = data[dic_key]

    # 将发送或接收到的所有参数按照参数名ASCII码从小到大排序（a-z），sign、sign_type、和空值不参与签名！
    sign_data = {k: v for k, v in sorted(sign_data.items())}

    # 将排序后的参数拼接成URL键值对的格式，例如 a=b&c=d&e=f，参数值不要进行url编码。
    param_string = "&".join([str(x) + "=" + str(sign_data[x]) for x in sign_data]) + get_config('epay_merchant_key')

    # 再将拼接好的字符串与商户密钥KEY进行MD5加密得出sign签名参数，sign = md5 ( a=b&c=d&e=f + KEY ) （注意：+ 为各语言的拼接符，不是字符！），md5结果为小写。
    return hashlib.md5(param_string.encode('utf-8')).hexdigest()
