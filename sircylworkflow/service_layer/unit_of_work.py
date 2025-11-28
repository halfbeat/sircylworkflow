# pylint: disable=attribute-defined-outside-init
from __future__ import annotations

import abc

from sircylclient.client import SircylClient

from rabbitmq import RabbitMQ
from sircylworkflow.securityutils import SymmetricKey


class UnitOfWork(abc.ABC):
    sircyl_client: SircylClient
    rabbitmq_client: RabbitMQ
    symmetric_key_instance: SymmetricKey

    def __enter__(self) -> UnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    def collect_new_events(self):
        pass

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class UnitOfWorkImpl(UnitOfWork):
    def __init__(self, sircyl_client, rabbitmq_client, symmetric_key_instance):
        self.sircyl_client = sircyl_client
        self.rabbitmq_client = rabbitmq_client
        self.symmetric_key_instance = symmetric_key_instance

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)

    def _commit(self):
        pass

    def rollback(self):
        pass
