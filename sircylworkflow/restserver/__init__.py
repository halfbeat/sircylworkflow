import argparse
import logging
import os
import sys
from logging.config import dictConfig

import urllib3
from flask import Flask
from logging_gelf.formatters import GELFFormatter
from logging_gelf.handlers import GELFTCPSocketHandler
from logging_gelf.schemas import GelfSchema
from marshmallow import fields
from sircylclient.client import SircylClient

from sircylworkflow.rabbitmq import RabbitMQ
from sircylworkflow.restserver.security import MyUsuario
from sircylworkflow.securityutils import SymmetricKey

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

parser = argparse.ArgumentParser(prog="rest-server",
                                 description="Servicios web para recubrir al Web Service de Sircyl")
parser.add_argument("--address", default=os.getenv('SERVICE_ADDRESS', "localhost"))
parser.add_argument("--port", "-P", help="Service port", type=int, default=os.getenv('SERVICE_PORT', "5000"))
parser.add_argument("--secret-key", help="Secret key para encriptado",
                    default=os.environ.get("SECRET_KEY",
                                           "123447a47f563e90fe2db0f56b1b17be62378e31b7cfd3adc776c59ca4c75e2fc512c15f69bb38307d11d5d17a41a7936789"))
parser.add_argument("--sircyl-url", help="URL del Servicio SirCyL",
                    default=os.environ.get("SIRCYL_URL",
                                           "http://preservicios.jcyl.es/ISicresJCYLWS/ISWebServiceDistributions?wsdl"))
parser.add_argument("--sircyl-username", help="Usuario SirCyL por defecto",
                    default=os.environ.get("SIRCYL_USERNAME", "usuprus4"))
parser.add_argument("--sircyl-password", help="Password SirCyL por defecto",
                    default=os.environ.get("SIRCYL_PASSWORD", "BuenVerano2023"))
parser.add_argument("--sircyl-max-call-per-minute", help="Maximo de llamadas por minuto", type=int,
                    default=int(os.environ.get("SIRCYL_CALLS_PER_MINUTE", "15")))
parser.add_argument("--rabbitmq-host", help="Host RabbitMQ por defecto",
                    default=os.environ.get("RABBITMQ_HOST", "albedodes.jcyl.es"))
parser.add_argument("--rabbitmq-port", help="Puerto RabbitMQ por defecto",
                    default=os.environ.get("RABBITMQ_PORT", "5672"))
parser.add_argument("--rabbitmq-vhost", help="Vhost RabbitMQ por defecto",
                    default=os.environ.get("RABBITMQ_VHOST", "SIRCYL"))
parser.add_argument("--rabbitmq-username", help="Usuario RabbitMQ por defecto",
                    default=os.environ.get("RABBITMQ_USERNAME", "sircyl"))
parser.add_argument("--rabbitmq-password", help="Password RabbitMQ por defecto",
                    default=os.environ.get("RABBITMQ_PASSWORD", "sircyl"))
parser.add_argument("--gelf-protocol", help="Protocolo para enviar logs a Graylog", default="tcp")
parser.add_argument("--gelf-host", help="Host para enviar logs a Graylog",
                    default=os.environ.get("GRAYLOG_HOST", "jcdkr27des101.ae.jcyl.es"))
parser.add_argument("--gelf-port", help="Puerto para enviar logs a Graylog",
                    default=os.environ.get("GRAYLOG_PORT", "32201"))

FLASK_SQLALCHEMY_ENGINE_OPTIONS = {'pool_size': 10, 'max_overflow': 20}

args = parser.parse_args()
symmetric_key_instance = SymmetricKey(args.secret_key)
sircyl_client = SircylClient(args.sircyl_url, args.sircyl_username, args.sircyl_password,
                             args.sircyl_max_call_per_minute)
rabbitmq_client = RabbitMQ(args.rabbitmq_username, args.rabbitmq_password, args.rabbitmq_host, args.rabbitmq_port,
                           args.rabbitmq_vhost, )

app = Flask(__name__, instance_relative_config=True)
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

from sircylworkflow.restserver.errorhandlers import *
from sircylworkflow.restserver.routes import *


def main():
    app.run(host=args.address, port=args.port)


if __name__ == "__main__":
    sys.exit(main())
