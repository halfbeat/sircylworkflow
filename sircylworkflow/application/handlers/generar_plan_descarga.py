import datetime as dt
import io
import json

from sircylclient.client import SircylClient
from sircylclient.port import FiltroAsientos
from sircylclient.serializer import Serializer

from sircylworkflow.application.commands import GenerarPlanDescargaCommand
from sircylworkflow.domain.model import FormatoDescarga
from sircylworkflow.domain.security import MyUsuario, Permisos
from sircylworkflow.messagebus import CommandHandler
from sircylworkflow.view.model import AsientoViewDto, PlanDescargaViewDto


class GenerarPlanDescargaHandler(CommandHandler):
    def __init__(self, sircyl_client: SircylClient, current_user: MyUsuario) -> None:
        super().__init__()
        self._current_user = current_user
        self._sircyl_client = sircyl_client

    def handle(self, cmd: GenerarPlanDescargaCommand):
        self._current_user.check_permiso(Permisos.GENERAR_PLAN_DESCARGA.value)
        username = self._current_user.sircyl_username
        password = self._current_user.sircyl_password

        filtro_asientos = FiltroAsientos(cmd.fecha_inicio, cmd.fecha_fin)
        with self._sircyl_client.with_credentials(username, password):
            asientos = self._sircyl_client.recuperar_asientos(filtro_asientos)
        if cmd.formato.value == FormatoDescarga.CSV.value:
            si = io.StringIO()
            serializer = Serializer.instance("csv", si)
            serializer.serialize(asientos)
            si.seek(0)
            return si.read()
        elif cmd.formato.value == FormatoDescarga.JSON.value:
            plan = PlanDescargaViewDto(
                id=f"{dt.datetime.now():%Y%m%d%H%M%S}",
                asientos=[
                    AsientoViewDto(
                        id=asiento.id_asiento,
                        fecha_distribucion=asiento.fecha_asiento,
                        materia=asiento.materia,
                        fecha_registro=asiento.fecha_registro,
                        numero_registro=asiento.numero_registro,
                        origen=asiento.origen,
                        destino=asiento.destino,
                        estado=asiento.estado,
                        fecha_estado=asiento.fecha_estado,
                    )
                    for asiento in asientos
                ],
            )

            return json.dumps(plan.model_dump(mode="json", exclude_none=True))
        else:
            raise ValueError(f"Formato de descarga no soportado: {cmd.formato}")
