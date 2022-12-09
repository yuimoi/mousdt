from flask import Flask
import config
from exts import db, scheduler, jwt, cache, log_handler, limiter


def create_app():
    from pay import bp as pay_bp
    from admin import bp as admin_bp
    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(pay_bp)
    app.register_blueprint(admin_bp)
    cache.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

    # app.logger.addHandler(log_handler())

    return app

