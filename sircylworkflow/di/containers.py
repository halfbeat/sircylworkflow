from dependency_injector import containers, providers
from sircylclient.client import SircylClient
from . import services


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=[".view"])
    config = providers.Configuration()
    sircyl_client = providers.Factory(SircylClient, ws_url=config.sircyl.ws_url)
    sircyl_service = providers.Factory(services.SircylService, sircyl_client)
