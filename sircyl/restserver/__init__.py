import argparse
import logging
import os
import sys
from logging.config import dictConfig

import urllib3
from flask import Flask
from marshmallow import fields
from logging_gelf.formatters import GELFFormatter
from logging_gelf.schemas import GelfSchema
from logging_gelf.handlers import GELFTCPSocketHandler

from securityutils import SymmetricKey
from sircylclient.client import SircylClient

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
parser.add_argument("--sircyl-username", help="Usuario SirCyL por defecto", default=os.environ.get("SIRCYL_USERNAME", "usuprus4"))
parser.add_argument("--sircyl-password", help="Password SirCyL por defecto", default=os.environ.get("SIRCYL_PASSWORD", "BuenVerano2023"))
parser.add_argument("--sircyl-max-call-per-minute", help="Maximo de llamadas por minuto", type=int,
                    default=int(os.environ.get("SIRCYL_CALLS_PER_MINUTE", "15")))

FLASK_SQLALCHEMY_ENGINE_OPTIONS = {'pool_size': 10, 'max_overflow': 20}

args = parser.parse_args()
symmetric_key_instance = SymmetricKey(args.secret_key)
sircyl_client = SircylClient(args.sircyl_url,args.sircyl_username, args.sircyl_password,args.sircyl_max_call_per_minute)

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

from errorhandlers import *
from routes import *

def main():
    app.run(host=args.address, port=args.port)

if __name__ == "__main__":
    sys.exit(main())