from authzclient.error import CredencialesRequeridas, PermisoRequerido, TokenJwtInvalido, TokenJwtRequerido
from flask import Flask

from sircylworkflow.error import BadParam, ErrorGenerico
from . import routes
from .errorhandlers import handle_bad_param, handle_credenciales_requeridas, handle_error_generico, \
    handle_permiso_requerido, handle_token_invalido, handle_token_requerido


def create_app():
    app = Flask(__name__)
    # Carga los parámetros de configuración desde variables de entorno
    app.config.from_prefixed_env()
    app.register_blueprint(routes.rest_services_blueprint)
    app.register_error_handler(BadParam, handle_bad_param)
    app.register_error_handler(ErrorGenerico, handle_error_generico)
    app.register_error_handler(TokenJwtInvalido, handle_token_invalido)
    app.register_error_handler(TokenJwtRequerido, handle_token_requerido)
    app.register_error_handler(CredencialesRequeridas, handle_credenciales_requeridas)
    app.register_error_handler(PermisoRequerido, handle_permiso_requerido)

    return app
