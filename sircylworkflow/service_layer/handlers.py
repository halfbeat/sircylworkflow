from __future__ import annotations

import csv
import datetime as dt
import io
import json
import logging

from sircylclient.port import FiltroAsientos
from sircylclient.serializer import Serializer

from sircylworkflow.constants import SIRCYL_EXCHANGE_NAME, SIRCYL_PLAN_EJECUCION_ROUTING_KEY, TTL_ASIENTOS_SEG
from sircylworkflow.domain import commands
from sircylworkflow.domain.commands import FormatoDescarga, EjecutarPlanDescargaCommand
from sircylworkflow.restserver import sircyl_client, symmetric_key_instance, rabbitmq_client
from sircylworkflow.globals import current_user
from sircylworkflow.di.infra.security import Permisos
from sircylworkflow.service_layer.view import PlanDescargaViewDto, AsientoViewDto


def generar_plan_descarga(cmd: commands.GenerarPlanDescargaCommand, uow=None):
    current_user.check_permiso(Permisos.GENERAR_PLAN_DESCARGA.value)
    username = current_user.sircyl_username
    password = current_user.sircyl_password

    filtro_asientos = FiltroAsientos(cmd.fecha_inicio, cmd.fecha_fin)
    with sircyl_client.with_credentials(username, password):
        asientos = sircyl_client.recuperar_asientos(filtro_asientos)
    if cmd.formato.value == FormatoDescarga.CSV.value:
        si = io.StringIO()
        serializer = Serializer.instance("csv", si)
        serializer.serialize(asientos)
        si.seek(0)
        return si
    elif cmd.formato.value == FormatoDescarga.JSON.value:
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
    else:
        raise ValueError(f"Formato de descarga no soportado: {cmd.formato}")

def ejecutar_plan_descarga(cmd: EjecutarPlanDescargaCommand, uow = None):
    current_user.check_permiso(Permisos.EJECUTAR_PLAN_DESCARGA.value)
    username = current_user.sircyl_username
    password = current_user.sircyl_password
    with sircyl_client.with_credentials(username, password) as client:
        reader = csv.reader(cmd.csv.splitlines(), delimiter=';', quotechar='"')
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
                    fecha_estado=dt.datetime.fromisoformat(row[8]))
                json_asiento = asiento.model_dump_json(exclude_none=True)
                headers = {
                    'plan_id': cmd.plan_id,
                    'asiento_id': asiento.id,
                    'materia': asiento.materia,
                    'origen': asiento.origen,
                    'destino': asiento.destino,
                    'estado': asiento.estado,
                    'registro': asiento.numero_registro,
                    'fecha_registro': asiento.fecha_registro.isoformat(),
                    'usuario_sircyl': symmetric_key_instance.encrypt(client._username.encode()),
                    'password_sircyl': symmetric_key_instance.encrypt(client._password.encode())
                }
                rabbitmq_client.publish(SIRCYL_EXCHANGE_NAME, SIRCYL_PLAN_EJECUCION_ROUTING_KEY, json_asiento,
                                         headers=headers, ttl=TTL_ASIENTOS_SEG*1000)
            except Exception as e:
                logging.warning(f"Error al procesar fila {row}: {e}")
                raise e
