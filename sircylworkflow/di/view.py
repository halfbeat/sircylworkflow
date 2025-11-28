import datetime
from dependency_injector.wiring import inject, Provide

from .services import SircylService
from .containers import Container


@inject
def index(sircyl_service: SircylService = Provide[Container.sircyl_service]):
    sircyl_service.buscar_asientos(datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(days=10))
    return "Hello, World!"
