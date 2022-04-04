import asyncio
import json
import typing
import uuid
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Optional

from aiohttp import web

from app.base.accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.base.application import Request


class WebSocketServiceMessageKind(Enum):
    INITIAL = "initial"


class WSConnectionNotFound(Exception):
    pass


@dataclass
class Event:
    kind: str
    payload: dict


class WSAccessor(BaseAccessor):
    class Meta:
        name = 'ws'

    def _init_(self):
        self._connections: dict[uuid.UUID, Any] = {}

    async def handle(self, request: 'Request'):
        ws_response = web.WebSocketResponse()
        await ws_response.prepare(request)
        connection_id = uuid.uuid4()
        self._connections[connection_id] = ws_response
        await self.store.geo.handle_open(str(connection_id))
        await self.read(id_=connection_id)
        await self.close(connection_id)
        return ws_response

    async def close(self, id_: uuid.UUID):
        try:
            await self._connections[id_].close()
        except KeyError:
            return None

        await self.store.geo.handle_close(str(id_))
        return None

    async def push(self, id_: typing.Union[str, uuid.UUID], event: Event):
        json_data = json.dumps(asdict(event))
        await self._push(uuid.UUID(id_), json_data)

    async def read(self, id_: uuid.UUID):
        async for message in self._connections[id_]:
            await self.store.geo.handle_event(json.loads(message.data))

    async def push_all(self, event: Event, except_of: Optional[list[str]] = None):
        if except_of is None:
            except_of = []
        json_data = json.dumps(asdict(event))
        await asyncio.gather(
            *[
                self._push(id_, json_data)
                for id_ in self._connections.keys()
                if str(id_) not in except_of
            ], return_exceptions=True,
        )

    async def _push(self, id_: uuid.UUID, data: str):
        try:
            await self._connections[id_].send_str(data)
        except KeyError:
            raise WSConnectionNotFound
        except ConnectionResetError:
            self._connections.pop(id_)
            await self.store.geo.handle_close(str(id_))
