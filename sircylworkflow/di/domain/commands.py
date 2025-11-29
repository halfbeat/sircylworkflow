# pylint: disable=too-few-public-methods
import abc
import dataclasses
import datetime
import typing
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Protocol, TypeVar, Generic

from sircylworkflow.di.domain.model import FormatoDescarga


class Command:
    pass

TCommand = TypeVar("TCommand", bound=Command)


class Handler(Generic[TCommand]):
    @abc.abstractmethod
    def handle(self, cmd: TCommand, ):
        raise NotImplementedError()

@dataclasses.dataclass
class Dispatcher:
    command_handlers: Dict[Command, Handler]

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
