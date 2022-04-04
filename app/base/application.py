import typing
from logging import Logger

from aiohttp import web

from app.store.store import Store


class Application(web.Application):
    store: "Store"
    logger: typing.Optional[Logger] = None


class Request(web.Request):
    user_id: str

    @property
    def app(self) -> "Application":
        return super().app


class View(web.View):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def app(self) -> "Application":
        return self.request.app

    @property
    def store(self) -> "Store":
        return self.app.store
