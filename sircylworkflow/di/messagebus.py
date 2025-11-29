# pylint: disable=broad-except
from __future__ import annotations

import logging
from typing import List, Dict, Callable, Type, Union

from sircylworkflow.di.services.sircylservice import SircylService

from .domain import events, commands

logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]


class MessageBus:
    def __init__(self, dispatcher: commands.Dispatcher) -> None:
        self._dispatcher = dispatcher

    def handle(
        self,
        message: Message,
    ):
        results = []
        queue = [message]
        while queue:
            message = queue.pop(0)
            if isinstance(message, events.Event):
                self.handle_event(message, queue)
            elif isinstance(message, commands.Command):
                cmd_result = self.handle_command(message, queue)
                results.append(cmd_result)
            else:
                raise ValueError(f"{message} was not an Event or Command")
        return results

    def handle_event(
        self,
        event: events.Event,
        queue: List[Message],
    ):
        if self.EVENT_HANDLERS.get(type(event)) is None:
            return

        for handler in self.EVENT_HANDLERS[type(event)]:
            try:
                logger.debug("handling event %s with handler %s", event, handler)
                handler(event)
            except Exception:
                logger.exception("Exception handling event %s", event)
                continue

    def handle_command(
        self,
        command: commands.Command,
        queue: List[Message],
    ):
        logger.debug("handling command %s", command)
        try:
            tc = type(command)
            handler = self._dispatcher.command_handlers[tc]
            result = handler.handle(command)
            return result
        except Exception:
            logger.exception("Exception handling command %s", command)
            raise

    EVENT_HANDLERS = {
        # events.OutOfStock: [handlers.send_out_of_stock_notification],
    }  # type: Dict[Type[events.Event], List[Callable]]

    COMMAND_HANDLERS = {
        # commands.GenerarPlanDescargaCommand: handlers.generar_plan_descarga,
        # commands.EjecutarPlanDescargaCommand: handlers.ejecutar_plan_descarga,
    }  # type: Dict[Type[commands.Command], Callable]
