import json

from authzclient.error import (
    CredencialesRequeridas,
    PermisoRequerido,
    TokenJwtInvalido,
    TokenJwtRequerido,
)
from flask import Response

from sircylworkflow.error import BadParam, ErrorGenerico
from sircylworkflow.constants import MIMETYPE_JSON
from sircylworkflow.view.model import ErrorViewDto


def handle_bad_param(e: BadParam):
    return Response(json.dumps(ErrorViewDto(codigo="E_BAD_PARAM", descripcion=str(e)).model_dump()), status=400,
                    mimetype=MIMETYPE_JSON)


def handle_error_generico(e: ErrorGenerico):
    return Response(json.dumps(ErrorViewDto(codigo="E_ERROR_GENERICO", descripcion=str(e)).model_dump()), status=500,
                    mimetype=MIMETYPE_JSON)


def handle_token_invalido(e: TokenJwtInvalido):
    return Response(json.dumps(ErrorViewDto(codigo="E_TOKEN_JWT_INVALIDO", descripcion=e.err).model_dump()), status=403,
                    mimetype=MIMETYPE_JSON)


def handle_token_requerido(e: TokenJwtRequerido):
    return Response(
        json.dumps(ErrorViewDto(codigo="TOKEN_JWT_REQUERIDO", descripcion="Se requiere un token JWT").model_dump()),
        status=401, mimetype=MIMETYPE_JSON)


def handle_credenciales_requeridas(e: CredencialesRequeridas):
    return Response(json.dumps(
        ErrorViewDto(codigo="CREDENCIALES_REQUERIDAS", descripcion="Se requieren credenciales").model_dump()),
        status=401, mimetype=MIMETYPE_JSON)


def handle_permiso_requerido(e: PermisoRequerido):
    return Response(json.dumps(ErrorViewDto(codigo="E_PERMISO_REQUERIDO", descripcion=str(e)).model_dump()), status=403,
                    mimetype=MIMETYPE_JSON)
