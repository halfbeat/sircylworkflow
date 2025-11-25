# pylint: disable=attribute-defined-outside-init
from __future__ import annotations

import abc


class AbstractUnitOfWork(abc.ABC):

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    def collect_new_events(self):
        # for sistema in self.sistemas.seen:
        #     while sistema.events:
        #         yield sistema.events.pop(0)
        pass

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

