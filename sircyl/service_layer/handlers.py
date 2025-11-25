from __future__ import annotations

import datetime as dt
import io
import json
from typing import TYPE_CHECKING

from sircylclient.port import FiltroAsientos
from sircylclient.serializer import Serializer

from domain import commands
from domain.commands import FormatoDescarga
from restserver import sircyl_client
from restserver.security import current_user, Permisos
from .view import PlanDescargaViewDto, AsientoViewDto

if TYPE_CHECKING:
    pass


def generar_plan_descarga(cmd: commands.GenerarPlanDescargaCommand, uow=None):
    current_user.check_permiso(Permisos.GENERAR_PLAN_DESCARGA.value)
    username = current_user.sircyl_username
    password = current_user.sircyl_password

    filtro_asientos = FiltroAsientos(cmd.fecha_inicio, cmd.fecha_fin)
    with sircyl_client.with_credentials(username, password):
        asientos = sircyl_client.recuperar_asientos(filtro_asientos)
    if cmd.formato == FormatoDescarga.CSV:
        si = io.StringIO()
        serializer = Serializer.instance("csv", si)
        serializer.serialize(asientos)
        si.seek(0)
        return si
    else:
        plan = PlanDescargaViewDto(
            id=f'{dt.datetime.now():%Y%m%d%H%M%S}',
            asientos=[AsientoViewDto(
                id=asiento.id_asiento,
                fecha_distribucion=asiento.fecha_asiento,
                materia=asiento.materia,
                fecha_registro=asiento.fecha_registro,
                numero_registro=asiento.numero_registro,
                origen=asiento.origen,
                destino=asiento.destino,
                estado=asiento.estado,
                fecha_estado=asiento.fecha_estado
            ) for asiento in asientos]
        )

        return json.dumps(plan.model_dump(mode="json", exclude_none=True))
