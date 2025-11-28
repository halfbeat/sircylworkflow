import datetime as dt
from sircylclient.client import SircylClient
from sircylclient.port import Asiento, FiltroAsientos


class SircylService:
    def __init__(self, sircyl_client: SircylClient) -> None:
        self._sircyl_client = sircyl_client

    def buscar_asientos(
        self, date_from: dt.datetime, date_to: dt.datetime
    ) -> list[Asiento]:
        return self._sircyl_client.recuperar_asientos(
            FiltroAsientos(date_from, date_to)
        )
