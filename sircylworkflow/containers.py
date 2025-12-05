import dataclasses

import jwt
from authzclient.authz import AuthzAdapter, AuthzConfig
from authzclient.error import TokenJwtInvalido
from authzclient.port import AuthorizationPort
from dependency_injector import containers, providers
from flask import request
from sircylclient.client import SircylClient

from application.commands import DescargarDocumentosAsientoCommand
from application.handlers.descargar_documentos_asiento import DescargarDocumentosAsientoHandler
from infra.rabbit.documents_parser_worker import DocumentsParserWorker
from infra.rabbit.sircyl_document_downloader_worker import SircylDocumentDownloaderWorker
from pathsecrets import PathSecrets
from rabbitmq import RabbitMQ
from sircylworkflow.application.authzmock import AuthzMock
from sircylworkflow.application.commands import (
    EjecutarPlanDescargaCommand,
    GenerarPlanDescargaCommand,
)
from sircylworkflow.application.handlers.ejecutar_plan_descarga import (
    EjecutarPlanDescargaHandler,
)
from sircylworkflow.application.handlers.generar_plan_descarga import (
    GenerarPlanDescargaHandler,
)
from sircylworkflow.application.services.sircylservice import SircylService
from sircylworkflow.domain.security import MyUsuario
from sircylworkflow.messagebus import TComandMap, TEventMap, MessageBus
from symetrickey import SymmetricKey


@dataclasses.dataclass
class Dispatcher:
    command_handlers: TComandMap
    event_handlers: TEventMap


def obtener_usuario_en_curso2(
        authz_port: AuthzAdapter, secrets: PathSecrets
) -> MyUsuario | None:
    secrets.get_value("OUAL")
    return None


def obtener_usuario_en_curso(
        authz_port: AuthorizationPort, secrets: PathSecrets, oauth2_public_key: str
) -> MyUsuario | None:
    token = request.headers.get("Authorization")
    if not token:
        return None
    try:
        parts = token.split(" ")
        if len(parts) != 2 or parts[0].upper() != "BEARER":
            raise TokenJwtInvalido("Invalid token. Unsupported Bearer")
        jwt_token = jwt.decode(
            parts[1], oauth2_public_key, algorithms=["RS256"], options={"verify_aud": False}
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
        calls_per_minute=config.sircyl.max_calls_per_minute,
    )
    # sircyl_client_factory = providers.Object(SircylClientMock())
    secrets_factory = providers.Factory(PathSecrets, config.secrets.path)
    current_user_factory = providers.Callable(
        obtener_usuario_en_curso, authz_port_factory, secrets_factory, config.oauth2.public_key
    )
    sircyl_service_factory = providers.Factory(
        SircylService, sircyl_client_factory, current_user_factory
    )
    rabbitmq_factory = providers.Factory(
        RabbitMQ,
        config.rabbitmq.host,
        config.rabbitmq.port,
        config.rabbitmq.username,
        config.rabbitmq.password,
        config.rabbitmq.vhost,
    )
    symmetric_key_instance = providers.Factory(
        SymmetricKey, secret=config.symmetric_key.secret_key
    )
    command_handlers_factory = providers.Dict(
        {
            GenerarPlanDescargaCommand: providers.Factory(
                GenerarPlanDescargaHandler,
                sircyl_client_factory,
                current_user_factory,
            ),
            EjecutarPlanDescargaCommand: providers.Factory(
                EjecutarPlanDescargaHandler,
                sircyl_client_factory,
                rabbitmq_factory,
                current_user_factory,
                symmetric_key_instance,
            ),
            DescargarDocumentosAsientoCommand: providers.Factory(
                DescargarDocumentosAsientoHandler,
                sircyl_client_factory,
                rabbitmq_factory,
                symmetric_key_instance
            )
        }
    )
    event_handler_factory = providers.Dict({})
    dispatcher_factory = providers.Factory(
        Dispatcher,
        command_handlers=command_handlers_factory,
        event_handlers=event_handler_factory,
    )
    messagebus_factory = providers.Factory(
        MessageBus, command_handlers_factory, event_handler_factory
    )
    sircyl_document_downloader_worker_factory = providers.Factory(
        SircylDocumentDownloaderWorker,
        rabbitmq_factory,
        config.workersettings.asientos_input_queue,
        sircyl_client_factory,
        config.workersettings.documents_output_exchange,
        symmetric_key_instance
    )

    sircyl_document_parser_worker_factory = providers.Factory(
        DocumentsParserWorker,
        rabbitmq_factory,
        config.workersettings.documentos_input_queue,
        config.workersettings.documentos_parseados_output_exchange
    )
