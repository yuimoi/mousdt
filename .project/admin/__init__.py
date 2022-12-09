from flask import Blueprint


bp = Blueprint("admin", __name__, url_prefix='/api/admin')

from . import views  # 注册蓝图时，bp是从这里导入的，视图函数需与蓝图放在一起，否则没有视图函数被注册，但也应注意，视图函数也从这里导入bp，所以该行应放在bp之后




from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from utils import restful
from flask import request
def admin_required(func):
    @jwt_required()  # 该带括号的装饰器直接加在视图函数或者内部有函数被装饰，则在错误的时候直接返回
    def jwt_required_func():
        pass

    @wraps(func)  # 保留func的属性以防止出错
    def inner(*args, **kwargs):
        last_string = str(request.url_rule).split("/")[-1]
        if last_string == "login" or last_string == "logout":
            return func(*args, **kwargs)

        jwt_required_func()
        identity = get_jwt_identity()  # 直接从header里拿token
        if 'admin' not in identity:
            return restful.permission_err(message='未登录')

        return func(*args, **kwargs)
    return inner


@bp.before_request
@admin_required
def admin_before_request():
    pass
