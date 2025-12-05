import argparse
import logging
import os
import sys
from logging.config import dictConfig

import constants
from containers import Container

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

parser = argparse.ArgumentParser(prog="worker",
                                 description="Worker RabbitMQ para la descarga de documentos relativos a un asienteo de SirCyL")
parser.add_argument(
    "--rabbitmq-host",
    help="Host RabbitMQ por defecto",
    default=os.environ.get("RABBITMQ_HOST", "albedodes.jcyl.es"),
)
parser.add_argument(
    "--rabbitmq-port",
    help="Puerto RabbitMQ por defecto",
    default=os.environ.get("RABBITMQ_PORT", "5672"),
)
parser.add_argument(
    "--rabbitmq-vhost",
    help="Vhost RabbitMQ por defecto",
    default=os.environ.get("RABBITMQ_VHOST", "SIRCYL"),
)
parser.add_argument(
    "--rabbitmq-username",
    help="Usuario RabbitMQ por defecto",
    default=os.environ.get("RABBITMQ_USERNAME", "sircyl"),
)
parser.add_argument(
    "--rabbitmq-password",
    help="Password RabbitMQ por defecto",
    default=os.environ.get("RABBITMQ_PASSWORD", "sircyl"),
)
parser.add_argument("--documentos-input-queue", help="Cola de entrada",
                    default=os.getenv('DOCUMENTOS_INPUT_QUEUE', constants.DOCUMENTOS_INPUT_QUEUE))
parser.add_argument("--documentos-parseados-output-exchange", help="Exchange donde enviar los documentos parseados`",
                    default=os.getenv('DOCUMENTOS_PARSEADOS_OUTPUT_EXCHANGE', constants.DOCUMENTOS_PARSEADOS_EXCHANGE))




def main():
    args = parser.parse_args()

    container = Container()

    container.config.rabbitmq.host.from_value(args.rabbitmq_host)
    container.config.rabbitmq.port.from_value(args.rabbitmq_port)
    container.config.rabbitmq.username.from_value(args.rabbitmq_username)
    container.config.rabbitmq.password.from_value(args.rabbitmq_password)
    container.config.rabbitmq.vhost.from_value(args.rabbitmq_vhost)

    container.config.workersettings.documentos_input_queue.from_value(args.documentos_input_queue)
    container.config.workersettings.documentos_parseados_output_exchange.from_value(args.documentos_parseados_output_exchange)

    try:
        worker = container.sircyl_document_parser_worker_factory()
        logging.info(f"Escuchando en la cola {args.documentos_input_queue}")
        worker.run(10, inactivity_timeout=10, auto_ack=False)
    except KeyboardInterrupt:
        logging.info("Interrupted")
    logging.info("Exiting")


if __name__ == "__main__":
    sys.exit(main())
