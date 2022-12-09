from . import bp
from flask import request, redirect, url_for, render_template, jsonify, g, current_app
from utils import function
from utils import scheduler
from models import OrderModel, TransferModel
import config
import time
from utils.function import order_paid_amount, get_config, decrypt, encrypt
import re
from utils import restful
from exts import db, cache


@bp.route('/',methods=['GET','POST'])
def index():
    return ""


@bp.route('/check_order', methods=['POST'])
def check_order():
    input_data = request.get_json()
    token = input_data.get('token')

    if token:
        try:
            order_id = int(decrypt(input_data['token'], get_config('encrypt_key')))
        except:
            return restful.params_err()
        order = OrderModel.query.filter( (OrderModel.id == order_id) ).first()

        if not order:
            return restful.params_err()

        if order.status == 1:
            return restful.ok(data={'status': 1, 'return_url': order.return_url})
        if order.status == -1:
            return restful.ok(data={'status': -1}, message='error')
        if order.status == 0:
            paid_transfer_list = TransferModel.query.filter(TransferModel.order_id == order.id).all()
            paid_transfer_list = [temp.to_dict() for temp in paid_transfer_list]


            return restful.ok(data={
                'status': 0,
                'order_price': order.price,
                'wallet_address': order.wallet_address,
                'network': order.network,
                'remain_time': order.end_time - int(time.time()),
                'transfer_items': paid_transfer_list
            })

    else:
        return restful.params_err()

@bp.route('/test/', methods=['GET', 'POST'])
def test():
    print(test1)

    return ""

