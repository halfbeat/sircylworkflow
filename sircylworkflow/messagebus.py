# pylint: disable=broad-except
from __future__ import annotations

import abc
import logging
from typing import Dict, Generic, List, TypeVar, Union

class Event:
    pass


class Command:
    pass


TCommand = TypeVar("TCommand", bound=Command)
TEvent = TypeVar("TEvent", bound=Event)
Message = Union[Command, Event]

class CommandHandler(Generic[TCommand]):
    @abc.abstractmethod
    def handle(
        self,
        cmd: TCommand,
    ):
        raise NotImplementedError()


class EventHandler(Generic[TEvent]):
    @abc.abstractmethod
    def handle(
        self,
        event: TEvent,
    ):
        raise NotImplementedError()

TComandMap = Dict[Command, CommandHandler]
TEventMap = Dict[Event, EventHandler]


logger = logging.getLogger(__name__)


class MessageBus:
    def __init__(self, command_handlers: TComandMap, event_handlers: TEventMap) -> None:
        self._command_handlers = command_handlers
        self._event_handlers = event_handlers

    def handle(
        self,
        message: Message,
    ):
        results = []
        queue = [message]
        while queue:
            message = queue.pop(0)
            if isinstance(message, Event):
                self.handle_event(message, queue)
            elif isinstance(message, Command):
                cmd_result = self.handle_command(message, queue)
                results.append(cmd_result)
            else:
                raise ValueError(f"{message} was not an Event or Command")
        return results

    def handle_event(
        self,
        event: Event,
        queue: List[Message],
    ):
        if self._event_handlers.get(type(event)) is None:
            return

        for handler in self._event_handlers[type(event)]:
            try:
                logger.debug("handling event %s with handler %s", event, handler)
                handler(event)
            except Exception:
                logger.exception("Exception handling event %s", event)
                continue

    def handle_command(
        self,
        command: Command,
        queue: List[Message],
    ):
        logger.debug("handling command %s", command)
        try:
            tc = type(command)
            handler = self._command_handlers[tc]
            result = handler.handle(command)
            return result
        except Exception:
            logger.exception("Exception handling command %s", command)
            raise
