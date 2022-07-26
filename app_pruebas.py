from flask import Flask
from app_lib.views.blueprint_v1.routes import blueprint as blueprint_views_v1
from app_lib.views.blueprint_v1.html_lib import add_methods_to_app
from app_lib.pruebas import run_extractor
from app_lib.log.log import get_log
import threading


__logger__ = get_log('app_pruebas')


app = Flask(__name__)
add_methods_to_app(app)
app.register_blueprint(blueprint_views_v1)
__logger__.info('Running thread')
threading.Thread(target=run_extractor).start()


if __name__ == '__main__':
    __logger__.info('Running app')
    app.run()
