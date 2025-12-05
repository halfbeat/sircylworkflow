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
parser.add_argument("--asientos-input-queue", help="Cola de entrada",
                    default=os.getenv('ASIENTOS_INPUT_QUEUE', constants.ASIENTOS_INPUT_QUEUE))
parser.add_argument("--documentos-output-exchange", help="Exchange donde mandar los documentos descargados",
                    default=os.getenv('DOCUMENTOS_OUTPUT_EXCHANGE', constants.SIRCYL_DOCUMENTOS_EXCHANGE))




def main():
    args = parser.parse_args()

    container = Container()

    container.config.symmetric_key.secret_key.from_value(args.secret_key)

    container.config.sircyl.ws_url.from_value(args.sircyl_url)
    container.config.sircyl.username.from_value(args.sircyl_username)
    container.config.sircyl.password.from_value(args.sircyl_password)
    container.config.sircyl.max_calls_per_minute.from_value(args.sircyl_max_call_per_minute)

    container.config.rabbitmq.host.from_value(args.rabbitmq_host)
    container.config.rabbitmq.port.from_value(args.rabbitmq_port)
    container.config.rabbitmq.username.from_value(args.rabbitmq_username)
    container.config.rabbitmq.password.from_value(args.rabbitmq_password)
    container.config.rabbitmq.vhost.from_value(args.rabbitmq_vhost)

    container.config.workersettings.asientos_input_queue.from_value(args.asientos_input_queue)
    container.config.workersettings.documents_output_exchange.from_value(args.documentos_output_exchange)

    try:
        worker = container.sircyl_document_downloader_worker_factory()
        logging.info(f"Escuchando en la cola {args.asientos_input_queue}")
        worker.run(10, inactivity_timeout=10, auto_ack=False)
    except KeyboardInterrupt:
        logging.info("Interrupted")
    logging.info("Exiting")


if __name__ == "__main__":
    sys.exit(main())
