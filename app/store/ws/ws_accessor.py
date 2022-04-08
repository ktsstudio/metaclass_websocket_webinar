import asyncio
import json
import typing
import uuid
from asyncio import Task
from dataclasses import asdict, dataclass
from typing import Any, Optional

from aiohttp import web

from app.base.accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.base.application import Request


class WSConnectionNotFound(Exception):
    pass


@dataclass
class Event:
    kind: str
    payload: dict


class WSAccessor(BaseAccessor):
    class Meta:
        name = 'ws'

    CONNECTION_TIMEOUT = 10

    def _init_(self):
        self._connections: dict[str, Any] = {}
        self._timeout_tasks: dict[str, Task] = {}

    async def handle_request(self, request: 'Request'):
        ws_response = web.WebSocketResponse()
        await ws_response.prepare(request)
        connection_id = str(uuid.uuid4())
        self._connections[connection_id] = ws_response
        self._refresh_timeout(connection_id)
        await self.store.geo.handle_open(str(connection_id))
        await self.read(connection_id)
        await self.close(connection_id)
        return ws_response

    async def close(self, connection_id: str):
        try:
            connection = self._connections.pop(connection_id)
            await connection.close()
        except KeyError:
            return None

        await self.store.geo.handle_close(str(connection_id))
        return None

    async def push(self, connection_id: str, event: Event):
        json_data = json.dumps(asdict(event))
        await self._push(connection_id, json_data)

    async def read(self, connection_id: str):
        async for message in self._connections[connection_id]:
            self._refresh_timeout(connection_id)
            raw_event = json.loads(message.data)
            await self.store.geo.handle_event(event=Event(
                kind=raw_event['kind'],
                payload=raw_event['payload'],
            ))

    async def push_all(self, event: Event, except_of: Optional[list[str]] = None):
        if except_of is None:
            except_of = []
        json_data = json.dumps(asdict(event))
        results = await asyncio.gather(
            *[
                self._push(id_, json_data)
                for id_ in self._connections.keys()
                if str(id_) not in except_of
            ], return_exceptions=True,
        )
        for result in results:
            if isinstance(result, Exception):
                self.logger.warning(result)

    async def _push(self, id_: str, data: str):
        try:
            await self._connections[id_].send_str(data)
        except KeyError:
            raise WSConnectionNotFound
        except ConnectionResetError:
            self._connections.pop(id_)
            raise

    def _refresh_timeout(self, connection_id: str):
        task = self._timeout_tasks.get(connection_id)
        if task:
            task.cancel()

        self._timeout_tasks[connection_id] = asyncio.create_task(self._close_by_timeout(connection_id))

    async def _close_by_timeout(self, connection_id: str):
        await asyncio.sleep(self.CONNECTION_TIMEOUT)
        await self.store.geo.handle_close(connection_id)
        await self.store.ws.close(connection_id)
