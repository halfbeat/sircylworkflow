from messagebus import MessageBus
from rabbitmq import RabbitMQWorker, RabbitMQ

class SircylDownloaderWorker(RabbitMQWorker):
    def __init__(self, rabbit: RabbitMQ, queue_name: str, messagebus: MessageBus):
        super().__init__(rabbit, queue_name)
        self.messagebus = messagebus

    def process_message(self, ch, method, properties, body):
        pass