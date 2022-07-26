from flask import Flask
from app_lib.views.blueprint_v1.routes import blueprint as blueprint_views_v1
from app_lib.views.blueprint_v1.html_lib import add_methods_to_app
from app_lib.app_main import run_extractor
import threading


app = Flask(__name__)
add_methods_to_app(app)
app.register_blueprint(blueprint_views_v1)
threading.Thread(target=run_extractor).start()


if __name__ == '__main__':
    app.run()
