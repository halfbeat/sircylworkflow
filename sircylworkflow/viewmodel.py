import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ErrorViewDto(BaseModel):
    codigo: str
    descripcion: str
    descripcionDetallada: Optional[str] = None


class FiltroFicherosViewDto(BaseModel):
    incluir: Optional[list[str]] = None
    excluir: Optional[list[str]] = None


class SolicitudDescargaDocumentosViewDto(BaseModel):
    fecha_inicio: datetime.datetime
    fecha_fin: datetime.datetime
    max_asientos: Optional[int] = None
    filtro_ficheros: Optional[FiltroFicherosViewDto] = FiltroFicherosViewDto()


class LocalizacionAsientoViewDto(BaseModel):
    id_carpeta: int
    id_archivo: int


class EstadoProcesamientoViewDto(str, Enum):
    NO_PROCESADO = 'NO_PROCESADO'
    PROCESADO = 'PROCESADO'
    NO_DISPONIBLE = 'NO_DISPONIBLE'
    NO_ENCONTRADO = 'NO_ENCONTRADO'
    ERROR = 'ERROR'


class AsientoViewDto(BaseModel):
    id: int
    fecha_distribucion: datetime.datetime
    materia: str
    fecha_registro: datetime.datetime
    numero_registro: str
    origen: str
    destino: str
    estado: str
    fecha_estado: Optional[datetime.datetime] = None
    localizacion: Optional[LocalizacionAsientoViewDto] = None
    estado_procesamiento: Optional[EstadoProcesamientoViewDto] = None
    numero_documentos: Optional[int] = None


class PlanDescargaViewDto(BaseModel):
    id: Optional[str] = None
    asientos: list[AsientoViewDto]
