import io
import json
import logging
import zipfile

from sircylclient.client import SircylClient, Asiento
from sircylclient.utils import slugify

from rabbitmq import RabbitMQWorker, RabbitMQ
from symetrickey import SymmetricKey
from viewmodel import AsientoViewDto


class DocumentsParserWorker(RabbitMQWorker):
    def __init__(self, rabbit: RabbitMQ, queue_name: str, output_exchange_name: str):
        super().__init__(rabbit, queue_name)
        self.output_exchange_name = output_exchange_name

    def process_message(self, ch, method, properties, body):
        print("Mensaje recibido")
        ch.basic_ack(delivery_tag=method.delivery_tag)