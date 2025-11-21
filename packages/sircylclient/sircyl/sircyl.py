import re
import time
from datetime import datetime

from zeep import Client
from zeep import xsd
from zeep.plugins import HistoryPlugin

from sircyl.limits import RateLimiter
from sircyl.port import SircylPort

DEFAULT_CALLS_PER_MINUTE = 4  # 4 peticiones por minuto

UsernameTokenHeader = xsd.Element(
    '{http://schemas.xmlsoap.org/ws/2002/04/secext}Security',
    xsd.ComplexType([
        xsd.Element(
            '{http://schemas.xmlsoap.org/ws/2002/04/secext}UsernameToken',
            xsd.ComplexType([
                xsd.Element(
                    '{http://schemas.xmlsoap.org/ws/2002/04/secext}Username', xsd.String()),
                xsd.Element(
                    '{http://schemas.xmlsoap.org/ws/2002/04/secext}Password', xsd.String()),
            ])
        )
    ])
)


class Estadisticas:
    def __init__(self):
        self.total_asientos = 0
        self.total_documentos = 0
        self.total_segundos = 0

    def add_asiento(self):
        self.total_asientos += 1

    def add_documento(self):
        self.total_documentos += 1

    def add_time(self, segundos):
        self.total_segundos += segundos

    def __str__(self):
        return f"total_asientos={self.total_asientos}, total_documentos={self.total_documentos}, total_segundos={self.total_segundos}"


class SircylAdapter(SircylPort):

    def __init__(self, ws_url: str, default_username: str = None, default_password: str = None,
                 calls_per_minute: int = DEFAULT_CALLS_PER_MINUTE):
        self.history = HistoryPlugin()
        self.client = Client(ws_url, plugins=[self.history])
        self.default_username = default_username
        self.default_password = default_password
        self.username = default_username
        self.password = default_password

        self.client.set_ns_prefix('wsse',
                                  "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd")
        self.estadisticas = Estadisticas()

        self.r1 = RateLimiter(calls_per_minute, 60)

    def get_history(self):
        return self.history

    def get_client(self):
        return self.client

    def recuperar_asientos(self, fecha_inicio: datetime, fecha_fin: datetime, num_registro_desde: int = 1,
                           num_registro_hasta: int = 100):
        response = self.client.service.WSLoadInputDistributions(fecha_inicio, fecha_fin, num_registro_desde,
                                                                num_registro_hasta,
                                                                _soapheaders=[self.build_security_header()])
        if response and response.List is None:
            response.List = type('', (object,), {"WSDistribution": []})()

        return response

    def iterate_asientos(self, fecha_inicio: datetime, fecha_fin: datetime, max_asientos: int = None,
                         tam_pagina: int = 50):
        start = time.time()
        response = self.recuperar_asientos(fecha_inicio, fecha_fin, 1, 0)
        total = response.Total or 0
        paginas = total // tam_pagina + 1
        idx = 0
        for pagina in range(0, paginas):
            if max_asientos and idx >= max_asientos:
                break
            try:
                response = self.recuperar_asientos(fecha_inicio, fecha_fin, 1 + pagina * tam_pagina, tam_pagina)
                for distribution in response.List.WSDistribution:
                    self.estadisticas.add_asiento()
                    if max_asientos and idx >= max_asientos:
                        break
                    yield distribution, None
                    idx += 1
            except Exception as e:
                yield None, e
        end = time.time()
        self.estadisticas.add_time(end - start)

    def _filtrar_documento(self, doc, page, incluir=None, excluir=None) -> bool:
        if incluir is None and excluir is None:
            return True
        incluir = [re.compile(expr) for expr in (incluir or [])]
        excluir = [re.compile(expr) for expr in (excluir or [])]
        esta_incluido = False
        esta_excluido = True
        for rgex_excluido in excluir:
            if rgex_excluido.search(page.Name):
                esta_excluido = True
                break
        for rgex_incluido in incluir:
            if rgex_incluido.search(page.Name):
                esta_incluido = True
        return (
                (esta_incluido and esta_excluido)
                or (esta_incluido and not esta_excluido)
                or (not esta_incluido and not esta_excluido)
        )

    def iterate_documentos(self, fecha_inicio: datetime, fecha_fin: datetime, incluir=None, excluir=None,
                           max_asientos: int = None, tam_pagina=50):
        start = time.time()
        response = self.recuperar_asientos(fecha_inicio, fecha_fin, 1, 0)
        total = response.Total
        paginas = total // tam_pagina + 1
        idx = 0
        for pagina in range(0, paginas):
            if max_asientos and idx >= max_asientos:
                break
            response = self.recuperar_asientos(fecha_inicio, fecha_fin, 1 + pagina * tam_pagina, tam_pagina)
            for distribution in response.List.WSDistribution:
                self.estadisticas.add_asiento()
                if max_asientos and idx >= max_asientos:
                    break
                try:
                    documents = self.descargar_documentos_asiento(distribution.Id)
                    for doc in documents:
                        self.estadisticas.add_documento()
                        if doc.Pages and doc.Pages.WSPage:
                            for page in doc.Pages.WSPage:
                                if self._filtrar_documento(doc, page, incluir, excluir):
                                    yield distribution, page, None
                except Exception as e:
                    yield None, None, e
                idx += 1
        end = time.time()
        self.estadisticas.add_time(end - start)

    def iterate_documentos_asiento(self, asiento_id, incluir=None, excluir=None):
        try:
            documents = self.descargar_documentos_asiento(asiento_id)
            for doc in documents:
                self.estadisticas.add_documento()
                if doc.Pages and doc.Pages.WSPage:
                    for page in doc.Pages.WSPage:
                        if self._filtrar_documento(doc, page, incluir, excluir):
                            yield asiento_id, page, None
        except Exception as e:
            yield None, None, e

    def descargar_documentos_asiento(self, asiento_id):
        self.r1.wait()

        documents = self.client.service.WSGetDocumentsDistributions(asiento_id, _soapheaders=[self.build_security_header()])
        if not documents or not documents.List or not documents.List.WSDocument:
            return []

        return documents.List.WSDocument

    def get_estadisticas(self):
        return self.estadisticas

    def set_username_and_password(self, username, password):
        self.username = username
        self.password = password

    def build_security_header(self):
        return UsernameTokenHeader(UsernameToken={'Username': self.username or self.default_username,
                                                  'Password': self.password or self.default_password})
