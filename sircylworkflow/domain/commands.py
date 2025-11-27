# pylint: disable=too-few-public-methods
import datetime
import typing
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Command:
    pass

class FormatoDescarga(Enum):
    CSV = 'csv'
    JSON = 'json'

@dataclass
class GenerarPlanDescargaCommand(Command):
    fecha_inicio: datetime.datetime
    fecha_fin: datetime.datetime
    formato: FormatoDescarga
    max_asientos: Optional[int] = None

@dataclass
class EjecutarPlanDescargaCommand(Command):
    plan_id: str
    csv: typing.TextIO
    max_asientos: Optional[int] = None