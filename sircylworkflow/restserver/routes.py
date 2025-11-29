import datetime as dt
import logging
from pathlib import Path

from flask import Blueprint
from flask import Response, request
from werkzeug.utils import secure_filename

from constants import MIMETYPE_CSV, MIMETYPE_JSON
from domain.commands import GenerarPlanDescargaCommand, FormatoDescarga, EjecutarPlanDescargaCommand
from error import BadParam
from sircylworkflow.di.infra.security import token_required
from service_layer import unit_of_work, messagebus
from service_layer.view import SolicitudDescargaDocumentosViewDto

rest_services_blueprint = Blueprint('rest_services', __name__, )

@rest_services_blueprint.route("/healthcheck", methods=["GET"])
def healthcheck():
    logging.info("UP!")
    return Response("OK", status=200, mimetype="text/plain")


@rest_services_blueprint.route("/api/v1/generarPlanDescarga", methods=["POST"])
@token_required
def generar_plan_descarga():
    solicitud_view = SolicitudDescargaDocumentosViewDto(**request.get_json())
    if request.headers.get("Accept") == MIMETYPE_CSV:
        formato = FormatoDescarga.CSV
    elif request.headers.get("Accept") == MIMETYPE_JSON:
        formato = FormatoDescarga.JSON
    else:
        raise ValueError(f"El formato {request.headers.get('Accept')} no está soportado")

    uow = unit_of_work.UnitOfWorkImpl()
    output = messagebus.handle(
        GenerarPlanDescargaCommand(solicitud_view.fecha_inicio, solicitud_view.fecha_fin, formato))[0]

    plan_id = f'{dt.datetime.now():%Y%m%d%H%M%S}'
    return Response(output, mimetype=request.headers.get("Accept"),
                    headers={"Content-disposition": f"fattachment; filename={plan_id}.{formato.value}"})


@rest_services_blueprint.route("/api/v1/ejecutarPlanDescarga", methods=["POST"])
@token_required
def ejecutar_plan_descarga():
    if 'file' not in request.files:
        raise BadParam('No file part')
    file = request.files['file']
    if file.filename == '':
        raise BadParam('No file part')
    filename = secure_filename(file.filename)
    plan_id = Path(filename).stem
    messagebus.handle(EjecutarPlanDescargaCommand(plan_id, file.read().decode('utf-8')))
    return '', 204
