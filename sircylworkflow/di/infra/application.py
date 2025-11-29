from flask import Flask

from ..view import routes


def create_app():
    app = Flask(__name__)
    # Carga los parámetros de configuración desde variables de entorno
    app.config.from_prefixed_env()
    app.add_url_rule("/", "index", routes.index)
    app.register_blueprint(routes.rest_services_blueprint)
    return app
