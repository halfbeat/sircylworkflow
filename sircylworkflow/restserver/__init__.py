import logging
from logging.config import dictConfig

import urllib3
from logging_gelf.formatters import GELFFormatter
from logging_gelf.handlers import GELFTCPSocketHandler
from logging_gelf.schemas import GelfSchema
from marshmallow import fields

from .containers import ApplicationContainer
# from routes import rest_services_blueprint
from sircylworkflow.di.infra.security import MyUsuario

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class JcylGelfSchema(GelfSchema):
    Componente = fields.String(dump_default="inventario-backend")
    Consejeria = fields.String(dump_default="gss")
    Entorno = fields.String()


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

container = ApplicationContainer()
app = container.app()
app.container = container
# app.register_blueprint(rest_services_blueprint)

# Carga los parámetros de configuración desde variables de entorno
app.config.from_prefixed_env()

# Configura los logs
gunicorn_error_logger = logging.getLogger('gunicorn.error')
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

gelf_handler = GELFTCPSocketHandler(host=app.config.get('GRAYLOG_HOST', 'localhost'),
                                    port=app.config.get('GRAYLOG_PORT', 12201))
gelf_handler.setFormatter(GELFFormatter(schema=JcylGelfSchema, null_character=True))

app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.handlers.extend([gelf_handler])

# from sircylworkflow.restserver.errorhandlers import *
# from sircylworkflow.restserver.routes import *
