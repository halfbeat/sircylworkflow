import abc
from datetime import datetime


class SircylPort(abc.ABC):
    @abc.abstractmethod
    def recuperar_asientos(self, fecha_inicio: datetime, fecha_fin: datetime, num_registro_desde: int = 1,
                           num_registro_hasta: int = 100):
        raise NotImplementedError

    @abc.abstractmethod
    def iterate_asientos(self, fecha_inicio: datetime, fecha_fin: datetime, max_asientos: int = None, tam_pagina=50):
       raise NotImplementedError

    @abc.abstractmethod
    def iterate_documentos(self, fecha_inicio: datetime, fecha_fin: datetime, max_asientos: int = None, tam_pagina=50):
      raise NotImplementedError

    @abc.abstractmethod
    def descargar_documentos_asiento(self, distribution):
        raise NotImplementedError