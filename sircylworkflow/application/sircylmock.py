import datetime as dt
from sircylclient.port import SircylPort, FiltroAsientos, FiltroDocumentos, Asiento

ASIENTOS = [
    Asiento(12345, dt.datetime(2025, 1, 12, 12, 20, 0), "UNA PRUEBA",
            dt.datetime(2025, 1, 12, 14, 00, 0), "2025393994883",
            "ORIGN", "DESTINO", "ARCHIVADO", dt.datetime(2025, 1, 12, 16, 20, 0))
]


class SircylClientMock(SircylPort):
    def recuperar_asientos(self, filtro: FiltroAsientos):
        return ASIENTOS

    def iasientos(self, filtro: FiltroAsientos, max_asientos: int = None, tam_pagina=50, ):
        for asiento in ASIENTOS:
            yield asiento, None

    def idocumentos(self, filtro: FiltroAsientos, filtro_documentos: FiltroDocumentos = None, max_asientos: int = None,
                    tam_pagina=50):
        raise NotImplementedError

    def idocsasiento(self, asiento, filtro_documentos: FiltroDocumentos = None):
        raise NotImplementedError

    def descargar_documentos_asiento(self, distribution):
        raise NotImplementedError
