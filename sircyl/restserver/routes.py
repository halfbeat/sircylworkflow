import datetime as dt
import logging

from flask import Response, request

from constants import MIMETYPE_CSV, MIMETYPE_JSON
from domain.commands import GenerarPlanDescargaCommand, FormatoDescarga
from restserver import app
from restserver.security import token_required
from service_layer.view import SolicitudDescargaDocumentosViewDto
from service_layer import messagebus


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    logging.info("UP!")
    return Response("OK", status=200, mimetype="text/plain")


@app.route("/api/v1/generarPlanDescarga", methods=["POST"])
@token_required
def generar_plan_descarga():
    solicitud_view = SolicitudDescargaDocumentosViewDto(**request.get_json())
    if request.headers.get("Accept") == MIMETYPE_CSV:
        formato = FormatoDescarga.CSV
    elif request.headers.get("Accept") == MIMETYPE_JSON:
        formato = FormatoDescarga.JSON
    else:
        raise ValueError(f"El formato {request.headers.get('Accept')} no está soportado")

    output = messagebus.handle(
        GenerarPlanDescargaCommand(solicitud_view.fecha_inicio, solicitud_view.fecha_fin, formato))[0]

    plan_id = f'{dt.datetime.now():%Y%m%d%H%M%S}'
    return Response(output, mimetype=request.headers.get("Accept"),
                    headers={"Content-disposition": f"fattachment; filename={plan_id}.{formato.value}"})
