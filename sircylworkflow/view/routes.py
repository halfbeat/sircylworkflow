import datetime as dt
import logging
from pathlib import Path

from flask import Blueprint, Response, request
from dependency_injector.wiring import inject, Provide
from werkzeug.utils import secure_filename

from sircylworkflow.constants import MIMETYPE_CSV, MIMETYPE_JSON
from sircylworkflow.application.commands import (
    EjecutarPlanDescargaCommand,
    GenerarPlanDescargaCommand,
)
from sircylworkflow.error import BadParam
from sircylworkflow.application.services.sircylservice import FormatoDescarga, SircylService

from ..containers import Container, MessageBus
from .model import SolicitudDescargaDocumentosViewDto


from flask import current_app as app

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
def generar_plan_descarga(
    messagebus: MessageBus = Provide[Container.messagebus_factory],
):
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


@rest_services_blueprint.route("/api/v1/ejecutarPlanDescarga", methods=["POST"])
# @token_required
@inject
def ejecutar_plan_descarga(
    messagebus: MessageBus = Provide[Container.messagebus_factory],
):
    if "file" not in request.files:
        raise BadParam("No file part")
    file = request.files["file"]
    filename = file.filename if file else None
    if not filename or filename == "":
        raise BadParam("No file part")
    filename = secure_filename(filename)
    plan_id = Path(filename).stem
    messagebus.handle(EjecutarPlanDescargaCommand(plan_id, file.read().decode("utf-8")))
    return "", 204

