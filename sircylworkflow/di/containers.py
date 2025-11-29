import datetime as dt
from dependency_injector.wiring import Provide, inject
import jwt
from authzclient.authz import AuthzAdapter, AuthzConfig
from authzclient.error import TokenJwtInvalido
from dependency_injector import containers, providers
from flask import current_app, request
from sircylclient.client import SircylClient

from sircylworkflow.customsecrets import Secrets
from sircylworkflow.di.application.authzmock import AuthzMock
from sircylworkflow.di.application.handlers import GenerarPlanDescargaHandler
from sircylworkflow.di.domain.commands import Dispatcher, GenerarPlanDescargaCommand
from sircylworkflow.di.domain.model import FormatoDescarga
from sircylworkflow.di.domain.security import MyUsuario

from .messagebus import MessageBus
from .services import sircylservice


def obtener_usuario_en_curso2(
    authz_port: AuthzAdapter, secrets: Secrets
) -> MyUsuario | None:
    secrets.get_value("OUAL")
    return None


def obtener_usuario_en_curso(
    authz_port: AuthzAdapter, secrets: Secrets
) -> MyUsuario | None:
    token = request.headers.get("Authorization")
    if not token:
        return None
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

    roles = authz_port.get_roles_principal(principal)
    username = secrets.get_value(f"{principal}_USER")
    password = secrets.get_value(f"{principal}_PASS")
    return MyUsuario(
        principal,
        roles,
        jwt_token,
        nombre,
        apellidos,
        email,
        dni_nie,
        username,
        password,
    )


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    authz_config_factory = providers.Factory(
        AuthzConfig,
        config.authz.aplicacion,
        config.authz.authz_uri,
        config.authz.jwt_token,
    )
    # authz_port_factory = providers.Factory(AuthzAdapter, config=authz_config_factory)
    authz_port_factory = providers.Object(AuthzMock())
    sircyl_client_factory = providers.Factory(
        SircylClient,
        ws_url=config.sircyl.ws_url,
        default_username=config.sircyl.username,
        default_password=config.sircyl.password,
    )

    secrets_factory = providers.Factory(Secrets, config.secrets.path)
    current_user_factory = providers.Callable(
        obtener_usuario_en_curso, authz_port_factory, secrets_factory
    )
    sircyl_service_factory = providers.Factory(
        sircylservice.SircylService, sircyl_client_factory, current_user_factory
    )
    handler_factory = providers.FactoryAggregate({})
    dispatcher_factory = providers.Factory(
        Dispatcher,
        command_handlers=providers.Dict(
            {
                GenerarPlanDescargaCommand: providers.Factory(
                    GenerarPlanDescargaHandler,
                    sircyl_client_factory,
                    current_user_factory,
                ),
            }
        ),
    )
    messagebus_factory = providers.Factory(MessageBus, dispatcher_factory)

