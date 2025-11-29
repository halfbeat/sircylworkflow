import datetime as dt
import logging

from flask import Blueprint, Response, request
from dependency_injector.wiring import inject, Provide

from sircylworkflow.constants import MIMETYPE_CSV, MIMETYPE_JSON
from sircylworkflow.di.domain.commands import GenerarPlanDescargaCommand
from sircylworkflow.di.messagebus import SircylService
from sircylworkflow.di.services.sircylservice import FormatoDescarga
from sircylworkflow.di.infra.security import token_required

from ..containers import Container, GenerarPlanDescargaHandler, MessageBus
from .model import SolicitudDescargaDocumentosViewDto


@inject
def index(
    sircyl_service: SircylService = Provide[Container.sircyl_service_factory],
):
    sircyl_service.buscar_asientos(
        dt.datetime.now(), dt.datetime.now() + dt.timedelta(days=10)
    )
    return "Hello, World!"


rest_services_blueprint = Blueprint(
    "rest_services",
    __name__,
)


@rest_services_blueprint.route("/healthcheck", methods=["GET"])
def healthcheck():
    logging.info("UP!")
    return Response("OK", status=200, mimetype="text/plain")


@rest_services_blueprint.route("/api/v1/generarPlanDescarga", methods=["POST"])
# @token_required
@inject
def generar_plan_descarga(messagebus: MessageBus = Provide[Container.messagebus_factory]):
    solicitud_view = SolicitudDescargaDocumentosViewDto(**request.get_json())
    if request.headers.get("Accept") == MIMETYPE_CSV:
        formato = FormatoDescarga.CSV
    elif request.headers.get("Accept") == MIMETYPE_JSON:
        formato = FormatoDescarga.JSON
    else:
        raise ValueError(
            f"El formato {request.headers.get('Accept')} no está soportado"
        )

    output = messagebus.handle(
        GenerarPlanDescargaCommand(
            solicitud_view.fecha_inicio, solicitud_view.fecha_fin, formato
        )
    )

    plan_id = f"{dt.datetime.now():%Y%m%d%H%M%S}"
    return Response(
        output,
        mimetype=request.headers.get("Accept"),
        headers={
            "Content-disposition": f"fattachment; filename={plan_id}.{formato.value}"
        },
    )
