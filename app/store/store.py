import typing

from app.store.geo.geo_manager import GeoManager
from app.store.ws.ws_accessor import WSAccessor

if typing.TYPE_CHECKING:
    from app.base.application import Application


class Store:
    def __init__(self, app: "Application"):
        self.app = app
        self.ws = WSAccessor(self)
        self.geo = GeoManager(self)
