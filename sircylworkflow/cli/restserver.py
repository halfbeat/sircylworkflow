import argparse
import os
import sys


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

from restserver import app

def main():
    args = parser.parse_args()
    container = app.container
    container.config.sircyl.sircyl_url.from_value(args.sircyl_url)
    container.config.sircyl.sircyl_username.from_value(args.sircyl_username)
    container.config.sircyl.sircyl_password.from_value(args.sircyl_password)
    container.config.sircyl.sircyl_max_call_per_minute.from_value(args.sircyl_max_call_per_minute)
    container.config.sircyl.tam_pagina.from_value(args.tam_pagina)

    container.config.rabbitmq.sircyl_url.from_value(args.sircyl_url)
    container.config.rabbitmq.sircyl_username.from_value(args.sircyl_username)
    container.config.rabbitmq.sircyl_password.from_value(args.sircyl_password)
    app.run(host=args.address, port=args.port)


if __name__ == "__main__":
    sys.exit(main())