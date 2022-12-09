import os
from cli import register_cli
from create_app import create_app
from first_run import first_run

app = create_app()
register_cli(app)

# FLASK_ENV判断是否是调试环境, FLASK_DEBUG判断pycharm是否关闭reloader运行,WERKZEUG_RUN_MAIN判断是否是reloader
if os.environ.get('FLASK_ENV') != 'development' or os.environ.get('FLASK_DEBUG') == '0' or os.environ.get(
        "WERKZEUG_RUN_MAIN") == "true":
    first_run(app)

if __name__ == '__main__':
    app.run()
