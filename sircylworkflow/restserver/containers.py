from dependency_injector import containers, providers
from dependency_injector.ext import flask
from flask import Flask
from sircylclient.client import SircylClient

from rabbitmq import RabbitMQ
from securityutils import SymmetricKey


class ApplicationContainer(containers.DeclarativeContainer):
    """Application container."""

    app = flask.Application(Flask, __name__)

    config = providers.Configuration()

    sircyl_client = providers.Factory(
        SircylClient,
        ws_url=config.sircyl.si.ws_url,
        default_username=config.sircyl.default_username,
        default_password=config.sircyl.default_password,
        calls_per_minute=config.sircyl.calls_per_minute,
        tam_pagina=config.sircyl.tam_pagina,
    )

    rabbitmq_client = providers.Factory(
        RabbitMQ,
        rabbitmq_username=config.rabbitmq.username,
        rabbitmq_password=config.rabbitmq.password,
        rabbitmq_host=config.rabbitmq.host,
        rabbitmq_port=config.rabbitmq.port,
        rabbitmq_vhost=config.rabbitmq.vhost
    )

    symmetric_key_instance = providers.Factory(
        SymmetricKey,
        secret_key = config.symmetric_key.secret_key
    )
