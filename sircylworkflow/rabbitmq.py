import logging
import os
from typing import Any, Callable

import pika
from pika.exceptions import ChannelClosed, StreamLostError
from pika.exchange_type import ExchangeType


class RabbitMQ:
    def __init__(self, user=None, password=None, host=None, port=None, vhost=None, ttl=None):
        self.user = user or os.getenv('RABBITMQ_USERNAME', 'user')
        self.password = password or os.getenv('RABBITMQ_PASSWORD', 'password')
        self.host = host or os.getenv('RABBITMQ_HOST', 'localhost')
        self.port = port or int(os.getenv('RABBITMQ_PORT', 5672))
        self.vhost = vhost or os.getenv("RABBITMQ_VHOST", "/")
        self.ttl = ttl
        self.connection = None
        self.channel = None

    def connect(self):
        credentials = pika.PlainCredentials(self.user, self.password)
        parameters = pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials,
                                               virtual_host=self.vhost)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def fixed_consume(self, queue_name: str, callback: Callable, max_num_messages: int, auto_ack: bool = True,
                      inactivity_timeout: float = None):
        """
        Método que recupera mensajes de una cola con capacidad de indicar timeout y/o un nº máximo de mensajes a leer.

        :param queue_name: Nombre de la cola de la que leer
        :param callback: función a llamar con el mensaje recibido
        :param max_num_messages: máximo nº de mensajes a procesar. None indica infinto
        :param auto_ack: Indica si se deben aceptar automáticamente los mensajes recibidos
        :param inactivity_timeout: Timeout de inactividad de la cola. None indica infinto
        """

        if not self.channel or self.channel.is_closed:
             self.connect()
        for method_frame, properties, body in self.channel.consume(queue_name, inactivity_timeout=inactivity_timeout):
            if not method_frame:
                break
            callback(self.channel, method_frame, properties, body)
            # Acknowledge the message
            if auto_ack:
                self.channel.basic_ack(method_frame.delivery_tag)
            # Escape out of the loop after 10 messages
            if method_frame.delivery_tag == max_num_messages:
                break
        # Cancel the consumer and return any pending messages
        self.channel.cancel()

    def consume(self, queue_name: str, callback: Callable, auto_ack: bool = True) -> Any:
        if not self.channel:
            self.connect()

        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=auto_ack)
        while True:
            try:
                self.channel.start_consuming()
            except (ChannelClosed, StreamLostError):
                logging.info("Channel closed. Reconnecting...")
                self.connect()
                self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=auto_ack)

    def publish(self, exchange_name, routing_key, message, headers=None, ttl=None):
        if not self.channel or self.channel.is_closed:
            self.connect()
        a_ttl = ttl or self.ttl
        self.channel.basic_publish(exchange=exchange_name,
                                   routing_key=routing_key,
                                   body=message,
                                   properties=pika.BasicProperties(
                                       delivery_mode=2,  # make message persistent,
                                       expiration=str(a_ttl) if a_ttl else None,
                                       headers=headers or {}
                                   ))

    def declare_queue(self, queue_name, durable=False):
        if not self.channel or self.channel.is_closed:
            self.connect()
        self.channel.queue_declare(queue=queue_name, durable=durable)

    def declare_exchange(self, exchange_name, exchange_type: ExchangeType | str = "direct", durable=False):
        if not self.channel or self.channel.is_closed:
            self.connect()
        self.channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=durable)

    def queue_bind(self, queue_name, exchange_name, routing_key):
        if not self.channel or self.channel.is_closed:
            self.connect()
        self.channel.queue_bind(queue_name, exchange_name, routing_key)

