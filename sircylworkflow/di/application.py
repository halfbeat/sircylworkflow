from flask import Flask
from .containers import Container
from . import view

def create_app():
    container = Container()
    container.config.sircyl.ws_url.from_value("https://google.com")
    
    app = Flask(__name__)
    app.container = container
    app.add_url_rule("/", "index", view.index)

    return app