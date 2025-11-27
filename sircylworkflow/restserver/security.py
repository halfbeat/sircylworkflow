import os
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from typing import Optional

import jwt
from authzclient.authz import AuthzAdapter
from authzclient.error import TokenJwtInvalido, TokenJwtRequerido
from authzclient.model import Usuario, Rol
from authzclient.port import AuthorizationPort
from flask import current_app
from flask import request

from customsecrets import Secrets
from .globals import _current_user_context_var


@dataclass(frozen=True)
class MyUsuario(Usuario):
    nombre: Optional[str]
    apellidos: Optional[str]
    email: Optional[str]
    documento_identidad: Optional[str]
    sircyl_username: Optional[str]
    sircyl_password: Optional[str]


_auth_port_singleton: AuthorizationPort | None = None

def instance_auth_port() -> AuthorizationPort:
    global _auth_port_singleton
    if _auth_port_singleton is None:
        _auth_port_singleton = AuthzAdapter(os.environ.get("AUTHZ_APLICACION"),
                                            os.environ.get("AUTHZ_URI"),
                                            os.environ.get("AUTHZ_TOKEN"))
    return _auth_port_singleton


class Roles(Enum):
    GESTOR = 'SRCL@APP'


class Permisos(Enum):
    GENERAR_PLAN_DESCARGA = 'asientos:generar_plan_descarga'
    CONSULTAR_ASIENTOS = 'asientos:consultar'
    DESCARGAR_DOCUMENTOS = 'asiento:descargar_documentos'
    EJECUTAR_PLAN_DESCARGA = 'asientos:ejecutar_plan_descarga'

def token_required(func):
    """
    Decorador Comprobación de que hay un token JWT y que confiamos en el
    :func: función a la que llamar si la comprobación es correcta
    :return: el propio decorador
    """

    @wraps(func)
    def decorated(*args, **kwargs):
        if current_app.config.get("AUTHENTICATION", 1) == 0:
            # Devuelvo un usuario con todos los permisos
            user = MyUsuario("superuser", roles=[], jwt_token=None, nombre=None, apellidos=None, email=None,
                             documento_identidad=None, sircyl_username=None, sircyl_password=None)
        else:
            token = request.headers.get("Authorization")
            if not token:
                raise TokenJwtRequerido()
            try:
                pk = current_app.config["OAUTH2_PUBLIC_KEY"]
                parts = token.split(" ")
                if len(parts) != 2 or parts[0].upper() != "BEARER":
                    raise TokenJwtInvalido("Invalid token. Unsupported Bearer")
                jwt_token = jwt.decode(
                    parts[1], pk, algorithms=["RS256"], options={"verify_aud": False}
                )
            except Exception as e:
                raise TokenJwtInvalido(str(e))

            principal = jwt_token.get("principal")
            if principal is None:
                principal = jwt_token.get("sub")
            nombre = jwt_token.get("given_name")
            apellidos = jwt_token.get("family_name")
            email = jwt_token.get("email")
            dni_nie = jwt_token.get("dni")

            if current_app.config.get("AUTHORIZATION", 1) == 0:
                roles = [Rol(Roles.GESTOR.value, [], [p.value for p in Permisos])]
            else:
                roles = instance_auth_port().get_roles_principal(principal)

            secrets_dir = current_app.config.get("SECRETS_DIR")
            secrets = Secrets(secrets_dir)
            usename = secrets.get_value(f"{principal}_USER")
            password = secrets.get_value(f"{principal}_PASS")
            user = MyUsuario(principal, roles, nombre, jwt_token, apellidos, email, dni_nie, usename, password)

        old_var = _current_user_context_var.set(user)
        current_app.logger.debug(f"Recuperada la información del usuario: {user}")
        result = func(*args, **kwargs)
        _current_user_context_var.reset(old_var)
        return result

    return decorated
