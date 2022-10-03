from logging import Logger

from aiohttp import web

from app.store import Store


class Application(web.Application):
    store: "Store"
    logger: Logger


class Request(web.Request):
    user_id: str

    @property
    def app(self) -> "Application":
        return super().app  # type: ignore


class View(web.View):
    @property
    def request(self) -> Request:
        return super().request  # type: ignore

    @property
    def app(self) -> "Application":
        return self.request.app

    @property
    def store(self) -> "Store":
        return self.app.store
