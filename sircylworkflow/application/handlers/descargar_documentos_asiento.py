from sircylclient.client import SircylClient

from application.commands import DescargarDocumentosAsientoCommand
from messagebus import CommandHandler
from rabbitmq import RabbitMQ
from symetrickey import SymmetricKey


class DescargarDocumentosAsientoHandler(CommandHandler):
    def __init__(
            self,
            sircyl_client: SircylClient,
            rabbitmq_client: RabbitMQ,
            symmetric_key_instance: SymmetricKey
    ) -> None:
        super().__init__()
        self._sircyl_client = sircyl_client
        self._rabbitmq_client = rabbitmq_client
        self._symmetric_key_instance = symmetric_key_instance

    def handle(self, cmd: DescargarDocumentosAsientoCommand):
        pass