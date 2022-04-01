import os

from aiohttp.abc import Application

from app import BASE_DIR
from app.core.views import ConnectView, IndexView


def setup_routes(app: Application):
    app.router.add_view("/connect", ConnectView)
    app.router.add_static("/static", os.path.join(BASE_DIR, "client", "static"))
    app.router.add_view("/", IndexView)
