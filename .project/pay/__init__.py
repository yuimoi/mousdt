from flask import Blueprint
bp = Blueprint("pay", __name__, url_prefix='/api/pay')

from . import views  # 注册蓝图时，bp是从这里导入的，视图函数需与蓝图放在一起，否则没有视图函数被注册，但也应注意，视图函数也从这里导入bp，所以该行应放在bp之后
from utils.SDK import *  # 导入SDK的视图函数
