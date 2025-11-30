# pylint: disable=too-few-public-methods
import datetime
import typing
from dataclasses import dataclass
from typing import Optional

from sircylworkflow.domain.model import FormatoDescarga
from sircylworkflow.messagebus import Command

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
