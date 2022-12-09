import os.path

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

from flask_caching import Cache

cache = Cache()

from flask_jwt_extended import JWTManager

jwt = JWTManager()
from utils import restful


@jwt.invalid_token_loader
def invalid_token_callback(jwt_payload):
    return restful.unlogin_err(message="invalid token")


@jwt.expired_token_loader
def expired_token_callback(jwt_payload):
    return restful.unlogin_err(message="expired token")


from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

import logging
from logging.handlers import RotatingFileHandler
from random import choice
from flask import request, has_request_context


# 日志不显示DEBUG是因为config里面的DEBUG为False，pycharm日志不显示ERROR需要把FLASK_DEBUG关掉
def log_handler():
    LOG_FORMAT = "[%(asctime)-15s] %(levelname)-6s in %(module)-8s %(message)s"
    log_dir = 'runtime/log'
    log_path = log_dir + '/log'

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    handler = RotatingFileHandler(log_path, encoding='utf-8', maxBytes=1000 * 1000 * 99, backupCount=5, delay=True)
    handler.setLevel(logging.ERROR)

    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    return handler
