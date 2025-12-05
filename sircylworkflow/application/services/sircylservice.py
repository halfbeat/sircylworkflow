import datetime as dt
import io
import json
from typing import Optional

from sircylclient.client import SircylClient
from sircylclient.port import Asiento, FiltroAsientos
from sircylclient.serializer import Serializer

from sircylworkflow.application.commands import FormatoDescarga
from sircylworkflow.domain.security import MyUsuario, Permisos
from sircylworkflow.viewmodel import AsientoViewDto, PlanDescargaViewDto


class SircylService:
    def __init__(self, sircyl_client: SircylClient, current_user: MyUsuario) -> None:
        self._sircyl_client = sircyl_client
        self._current_user = current_user

    def buscar_asientos(
        self, date_from: dt.datetime, date_to: dt.datetime
    ) -> list[Asiento]:
        return self._sircyl_client.recuperar_asientos(
            FiltroAsientos(date_from, date_to)
        )

    def generar_plan_descarga(
        self,
        fecha_inicio: dt.datetime,
        fecha_fin: dt.datetime,
        formato: FormatoDescarga,
        max_asientos: Optional[int] = None,
    ):
        self._current_user.check_permiso(Permisos.GENERAR_PLAN_DESCARGA.value)
        username = self._current_user.sircyl_username
        password = self._current_user.sircyl_password

        filtro_asientos = FiltroAsientos(fecha_inicio, fecha_fin)
        with self._sircyl_client.with_credentials(username, password):
            asientos = self._sircyl_client.recuperar_asientos(filtro_asientos)
        if formato.value == FormatoDescarga.CSV.value:
            si = io.StringIO()
            serializer = Serializer.instance("csv", si)
            serializer.serialize(asientos)
            si.seek(0)
            return si
        elif formato.value == FormatoDescarga.JSON.value:
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
            raise ValueError(f"Formato de descarga no soportado: {formato}")
