from exts import db
from sqlalchemy.orm import relationship
import requests
import config
import time
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import event
from werkzeug.security import generate_password_hash
from utils import SDK


# 多个transfer对应一个order
# 多个order对应一个wallet
class OrderModel(db.Model, SerializerMixin):
    __tablename__ = 'order'

    serialize_rules = ('-wallet',)

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    notify_type = db.Column(db.String(20), nullable=False)
    merchant_id = db.Column(db.Integer, nullable=False, default=0)
    merchant_order_id = db.Column(db.String(50), nullable=False)
    merchant_good_name = db.Column(db.String(50), nullable=False)
    currency = db.Column(db.String(20), nullable=False, default="USDT")
    network = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    paid_price = db.Column(db.Float(), nullable=False, default=0)
    notify_url = db.Column(db.String(255), nullable=False)
    return_url = db.Column(db.String(255), nullable=False)

    wallet_address = db.Column(db.String(100), nullable=False)
    create_time = db.Column(db.Integer(), nullable=False)
    end_time = db.Column(db.Integer(), nullable=False)
    status = db.Column(db.Integer(), nullable=False, default=0)

    # 一对多条件：
    # 1.使用这个必须在多的一方创建外键ForeignKey
    # 2.在一的那一方，建立跟多的那一方的关联属性
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)

    # 表上看不到的字段，表示关联
    transfers = db.relationship("TransferModel", backref="order")

    def create(self):
        from utils.function import free_wallet
        # from util.scheduler import start_check_job

        # 检查是否有钱包空闲
        wallet = free_wallet(network=self.network)
        if wallet is None:
            return None

        self.wallet_address = wallet.address

        # 查询商户订单是否重复，重复返回查询到的，不重复创建新订单的并返回
        result = OrderModel.query.filter(
                    (OrderModel.merchant_order_id == self.merchant_order_id) &
                    (OrderModel.merchant_id == self.merchant_id)
        ).first()
        if result is None:
            self.wallet_id = wallet.id
            wallet.status = 0
            wallet.start_lock_time = int(time.time())
            wallet.end_lock_time = int(self.end_time)

            db.session.add(self)
            db.session.commit()

            # start_check_job()

            return self
        else:
            order = result
            return order

    def order_success(self, transfer):
        # 标记订单为已完成
        OrderModel.query.filter(OrderModel.id == self.id).update({"status": 1})

        # 关联订单和交易记录
        self.transfer = transfer
        db.session.commit()

        # 发送回调
        self.notify()

    def notify(self):
        getattr(SDK, self.notify_type).notify(self)


class AdminModel(db.Model, SerializerMixin):
    serialize_rules = ("-_password",)
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    _password = db.Column(db.String(255), nullable=False)

    # create_time = db.Column(db.Integer(), nullable=False)
    # create_ip = db.Column(db.String(50), nullable=False)
    # login_time = db.Column(db.Integer, nullable=True)
    # login_ip = db.Column(db.String(50), nullable=True)

    def __init__(self, *args, **kwargs):
        # @password.setter管不到初始化，所以初始化也要写一次
        if "password" in kwargs:
            self.password = kwargs.get("password")
            kwargs.pop("password")
        super(AdminModel, self).__init__(*args, **kwargs)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, real_password):
        self._password = generate_password_hash(real_password)

    def create(self):
        db.session.add(self)
        db.session.commit()

        return self


class TransferModel(db.Model, SerializerMixin):
    # order和transfer是one to many 绑定，必须要有一边将关联属性从序列化中排除，否则两边调用都会无限递归
    serialize_rules = ('-order',)
    __tablename__ = 'transfer'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    currency = db.Column(db.String(20), nullable=False)
    network = db.Column(db.String(20), nullable=False)
    transaction_id = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Float(), nullable=False)
    create_time = db.Column(db.Integer(), nullable=False)
    from_address = db.Column(db.String(100), nullable=False)
    to_address = db.Column(db.String(100), nullable=False)
    message = db.Column(db.String(100), nullable=True)
    purpose = db.Column(db.String(100), nullable=False, default='receive')

    # 一对多条件：
    # 1.使用这个必须在多的一方创建外键ForeignKey
    # 2.在一的那一方，建立跟多的那一方的关联属性
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)


class WalletModel(db.Model, SerializerMixin):
    # 一个钱包对应非常多个订单，需要时再主动查询
    serialize_rules = ('-secret', '-orders')

    __tablename__ = 'wallet'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    network = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(100), nullable=False, unique=True)
    secret = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Integer(), nullable=False, default=1)
    balance = db.Column(db.Float(), nullable=False, default=0)
    fee_balance = db.Column(db.Float(), nullable=False, default=0)
    start_lock_time = db.Column(db.Integer(), nullable=True)
    end_lock_time = db.Column(db.Integer(), nullable=True)
    refresh_time = db.Column(db.Integer(), nullable=True)
    priority = db.Column(db.Integer, nullable=False, default=1)
    purpose = db.Column(db.String(100), nullable=False, default='receive')

    # 表上看不到的字段，表示关联
    orders = db.relationship("OrderModel", backref="wallet")

    @classmethod
    def query_order(cls):
        return cls.priority.desc(), cls.balance.desc(), cls.id.asc()


class ConfigModel(db.Model, SerializerMixin):
    __tablename__ = 'config'
    key = db.Column(db.String(255), nullable=False, primary_key=True)
    value = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(255), nullable=True)

    @classmethod
    def get_all(cls):
        config_list = cls.query.all()
        result = {}
        for i in config_list:
            result[i.key] = i.value
        return result
