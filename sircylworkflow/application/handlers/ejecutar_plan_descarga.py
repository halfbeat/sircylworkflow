import csv
import datetime as dt
import logging

from sircylclient.client import SircylClient

from sircylworkflow.constants import SIRCYL_EXCHANGE_NAME, SIRCYL_PLAN_EJECUCION_ROUTING_KEY, TTL_ASIENTOS_SEG
from sircylworkflow.application.commands import EjecutarPlanDescargaCommand
from sircylworkflow.domain.security import MyUsuario, Permisos
from sircylworkflow.rabbitmq import RabbitMQ
from sircylworkflow.messagebus import CommandHandler
from sircylworkflow.symetrickey import SymmetricKey
from sircylworkflow.view.model import AsientoViewDto


class EjecutarPlanDescargaHandler(CommandHandler):
    def __init__(
        self,
        sircyl_client: SircylClient,
        rabbitmq_client: RabbitMQ,
        current_user: MyUsuario,
        symmetric_key_instance: SymmetricKey,
    ) -> None:
        super().__init__()
        self._sircyl_client = sircyl_client
        self._rabbitmq_client = rabbitmq_client
        self._current_user = current_user
        self._symmetric_key_instance = symmetric_key_instance

    def handle(self, cmd: EjecutarPlanDescargaCommand):
        self._current_user.check_permiso(Permisos.EJECUTAR_PLAN_DESCARGA.value)
        username = self._current_user.sircyl_username
        password = self._current_user.sircyl_password
        with self._sircyl_client.with_credentials(username, password) as client:
            reader = csv.reader(cmd.csv.splitlines(), delimiter=";", quotechar='"')
            for row in reader:
                try:
                    asiento = AsientoViewDto(
                        id=int(row[0]),
                        fecha_distribucion=dt.datetime.fromisoformat(row[2]),
                        materia=row[7],
                        fecha_registro=dt.datetime.fromisoformat(row[3]),
                        numero_registro=row[4],
                        origen=row[5],
                        destino=row[6],
                        estado=row[1],
                        fecha_estado=dt.datetime.fromisoformat(row[8]),
                    )
                    json_asiento = asiento.model_dump_json(exclude_none=True)
                    headers = {
                        "plan_id": cmd.plan_id,
                        "asiento_id": asiento.id,
                        "materia": asiento.materia,
                        "origen": asiento.origen,
                        "destino": asiento.destino,
                        "estado": asiento.estado,
                        "registro": asiento.numero_registro,
                        "fecha_registro": asiento.fecha_registro.isoformat(),
                        "usuario_sircyl": self._symmetric_key_instance.encrypt(
                            client._username.encode()
                        ) if client._username else None,
                        "password_sircyl": self._symmetric_key_instance.encrypt(
                            client._password.encode()
                        ) if client._password else None,
                    }
                    self._rabbitmq_client.publish(
                        SIRCYL_EXCHANGE_NAME,
                        SIRCYL_PLAN_EJECUCION_ROUTING_KEY,
                        json_asiento,
                        headers=headers,
                        ttl=TTL_ASIENTOS_SEG * 1000,
                    )
                except Exception as e:
                    logging.warning(f"Error al procesar fila {row}: {e}")
                    raise e
