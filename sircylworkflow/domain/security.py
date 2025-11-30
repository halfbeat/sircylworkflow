from dataclasses import dataclass
from enum import Enum
from typing import Optional

from authzclient.model import Usuario


class Roles(Enum):
    GESTOR = "SRCL@APP"


class Permisos(Enum):
    GENERAR_PLAN_DESCARGA = "asientos:generar_plan_descarga"
    CONSULTAR_ASIENTOS = "asientos:consultar"
    DESCARGAR_DOCUMENTOS = "asiento:descargar_documentos"
    EJECUTAR_PLAN_DESCARGA = "asientos:ejecutar_plan_descarga"

@dataclass(frozen=True)
class MyUsuario(Usuario):
    nombre: Optional[str]
    apellidos: Optional[str]
    email: Optional[str]
    documento_identidad: Optional[str]
    sircyl_username: Optional[str]
    sircyl_password: Optional[str]