import logging
from logging import getLogger

from aiohttp import web

from app.base.application import Application
from app.core.routes import setup_routes
from app.store import Store


def create_app() -> Application:
    app = web.Application()
    logging.basicConfig(level=logging.INFO)
    app.logger = getLogger()
    app.store = Store(app)
    setup_routes(app)
    return app


if __name__ == '__main__':
    web.run_app(create_app(), port=8000)
