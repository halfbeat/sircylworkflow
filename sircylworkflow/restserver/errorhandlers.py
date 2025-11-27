import json

from authzclient.error import CredencialesRequeridas, TokenJwtInvalido, TokenJwtRequerido, PermisoRequerido
from flask import Response

from constants import MIMETYPE_JSON
from error import BadParam, ErrorGenerico
from restserver import app
from service_layer.view import ErrorViewDto


@app.errorhandler(BadParam)
def handle_error_generico(e: BadParam):
    return Response(json.dumps(ErrorViewDto(codigo="E_BAD_PARAM", descripcion=str(e)).model_dump()), status=400,
                    mimetype=MIMETYPE_JSON)


@app.errorhandler(ErrorGenerico)
def handle_error_generico(e: ErrorGenerico):
    return Response(json.dumps(ErrorViewDto(codigo="E_ERROR_GENERICO", descripcion=str(e)).model_dump()), status=500,
                    mimetype=MIMETYPE_JSON)


@app.errorhandler(TokenJwtInvalido)
def handle_token_invalido(e: TokenJwtInvalido):
    return Response(json.dumps(ErrorViewDto(codigo="E_TOKEN_JWT_INVALIDO", descripcion=e.err).model_dump()), status=403,
                    mimetype=MIMETYPE_JSON)


@app.errorhandler(TokenJwtRequerido)
def handle_token_requerido(e: TokenJwtRequerido):
    return Response(
        json.dumps(ErrorViewDto(codigo="TOKEN_JWT_REQUERIDO", descripcion="Se requiere un token JWT").model_dump()),
        status=401, mimetype=MIMETYPE_JSON)


@app.errorhandler(CredencialesRequeridas)
def handle_credenciales_requeridas(e: CredencialesRequeridas):
    return Response(json.dumps(
        ErrorViewDto(codigo="CREDENCIALES_REQUERIDAS", descripcion="Se requieren credenciales").model_dump()),
        status=401, mimetype=MIMETYPE_JSON)


@app.errorhandler(PermisoRequerido)
def handle_credenciales_requeridas(e: PermisoRequerido):
    return Response(json.dumps(ErrorViewDto(codigo="E_PERMISO_REQUERIDO", descripcion=str(e)).model_dump()), status=403,
                    mimetype=MIMETYPE_JSON)
