from flask import jsonify


class HttpCode(object):
    # 响应正常
    ok  = 200
    # 没有登录
    unlogin_err = 401
    # 没有权限
    permission_err = 403
    # 客户端参数错误
    params_err = 400
    # 服务器错误
    server_err = 500


def _restful_result(code, message, data):
    return jsonify({"msg": message or "", "data": data or {}, "code": code}), code


def ok(message="ok", data=None):
    return _restful_result(code=HttpCode.ok, message=message, data=data)


def unlogin_err(message="unlogin"):
    return _restful_result(code=HttpCode.unlogin_err, message=message, data=None)


def permission_err(message="No permission"):
    return _restful_result(code=HttpCode.permission_err, message=message, data=None)


def params_err(message="Params error"):
    return _restful_result(code=HttpCode.params_err, message=message, data=None)


def server_err(message="Server error"):
    return _restful_result(code=HttpCode.server_err, message=message, data=None)
