import os
import datetime

BASE_DIR = os.path.dirname(__file__)

# DEBUG为False时，DEBUG级别的日志无法生成
DEBUG = False

SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db' #此为相对路径

SQLALCHEMY_TRACK_MODIFICATIONS = False  # 如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。这需要额外的内存， 如果不必要的可以禁用它。
JSON_AS_ASCII = False

SECRET_KEY_PATH = os.path.join(BASE_DIR, 'runtime', '.SECRET_KEY')
if not os.path.exists(os.path.join(BASE_DIR, 'runtime')):
    os.makedirs(os.path.join(BASE_DIR, 'runtime'))
if not os.path.exists(SECRET_KEY_PATH):
    SECRET_KEY = os.urandom(24).hex()
    with open(SECRET_KEY_PATH, 'w+') as f:
        f.write(SECRET_KEY)
else:
    with open(SECRET_KEY_PATH, 'r') as f:
        SECRET_KEY = f.read()

JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=7)

wallet_listener_interval = 10


# # Flask-Caching的配置
CACHE_TYPE = 'filesystem'  # 使用文件系统来存储缓存的值，重启flask不清空
CACHE_THRESHOLD = 10000
CACHE_DIR = os.path.join(BASE_DIR, "runtime", "cache")  # 文件目录

CACHE_DEFAULT_TIMEOUT = 600
# if os.name == 'nt':
#     # CACHE_TYPE = 'simple'  # 使用本地python字典进行存储，线程非安全，不适用scheduler，不同的scheduler之间无法共用
#     CACHE_TYPE = 'filesystem'  # 使用文件系统来存储缓存的值，重启flask不清空
#     CACHE_THRESHOLD = 10000
#     CACHE_DIR = os.path.join(BASE_DIR, "runtime", "flask-cache")  # 文件目录
#
# else:
#     CACHE_TYPE = "RedisCache"
#     CACHE_REDIS_HOST = "127.0.0.1"
#     CACHE_REDIS_PORT = 6379
#     # CACHE_TYPE = 'redis'  # 使用redis作为缓存
#     # CACHE_KEY_PREFIX  # 设置cache_key的前缀
#     # CACHE_REDIS_HOST  # redis地址
#     # CACHE_REDIS_PORT  # redis端口
#     # CACHE_REDIS_PASSWORD  # redis密码
#     # CACHE_REDIS_DB  # 使用哪个数据库
#     # # 也可以一键配置
#     # CACHE_REDIS_URL

