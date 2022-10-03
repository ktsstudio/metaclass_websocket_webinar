import asyncio
import json
import typing
import uuid
from asyncio import Task, CancelledError
from dataclasses import dataclass, asdict

from aiohttp.web_ws import WebSocketResponse

from app.base.accessor import BaseAccessor
from app.base.utils import do_by_timeout_wrapper

if typing.TYPE_CHECKING:
    from app.base.application import Request


@dataclass
class Event:
    kind: str
    payload: dict

    def __str__(self):
        return f'Event<{self.kind}>'


class WSContext:
    def __init__(
            self,
            accessor: 'WSAccessor',
            request: 'Request',
            close_callback: typing.Callable[[str], typing.Awaitable] | None = None,
    ):
        self._accessor = accessor
        self._request = request
        self.connection_id: typing.Optional[str] = None
        self._close_callback = close_callback

    async def __aenter__(self) -> str:
        self.connection_id = await self._accessor.open(self._request, close_callback=self._close_callback)
        return self.connection_id

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._accessor.close(self.connection_id)


@dataclass
class Connection:
    session: WebSocketResponse
    timeout_task: Task
    close_callback: typing.Callable[[str], typing.Awaitable] | None


class WSAccessor(BaseAccessor):
    class Meta:
        name = 'ws_accessor'

    CONNECTION_TIMEOUT_SECONDS = 15

    def _init_(self) -> None:
        self._connections: dict[str, Connection] = {}

    async def open(
            self,
            request: 'Request',
            close_callback: typing.Callable[[str], typing.Awaitable[typing.Any]] | None = None,
    ) -> str:
        ws_response = WebSocketResponse()
        await ws_response.prepare(request)
        connection_id = str(uuid.uuid4())

        self.logger.info(f'Handling new connection with {connection_id=}')

        self._connections[connection_id] = Connection(
            session=ws_response,
            timeout_task=self._create_timeout_task(connection_id),
            close_callback=close_callback,
        )
        return connection_id

    def _create_timeout_task(self, connection_id: str) -> Task:
        def log_timeout(result: Task):
            try:
                exc = result.exception()
            except CancelledError:
                return

            if exc:
                self.logger.error('Can not close connection by timeout', exc_info=result.exception())
            else:
                self.logger.info(f'Connection with {connection_id=} was closed by inactivity')

        task = asyncio.create_task(
            do_by_timeout_wrapper(
                self.close,
                self.CONNECTION_TIMEOUT_SECONDS,
                args=[connection_id],
            )
        )
        task.add_done_callback(log_timeout)
        return task

    async def close(self, connection_id: str):
        connection = self._connections.pop(connection_id, None)
        if not connection:
            return

        self.logger.info(f'Closing {connection_id=}')

        if connection.close_callback:
            await connection.close_callback(connection_id)

        if not connection.session.closed:
            await connection.session.close()

    async def push(self, event: Event, connection_id: str):
        data = json.dumps(asdict(event), separators=(',', ':'))
        return await self._push(self._connections[connection_id].session, data=data)

    async def _push(self, connection: 'WebSocketResponse', data: str):
        await connection.send_str(data)

    async def stream(self, connection_id: str) -> typing.AsyncIterable[Event]:
        async for message in self._connections[connection_id].session:
            await self.refresh_connection(connection_id)
            data = message.json()  # noqa
            yield Event(kind=data['kind'], payload=data['payload'])

    async def broadcast(self, event: Event, except_of: list[str] | None = None):
        self.logger.info(f'Broadcasting {event} for all except of {except_of}')
        ops = []
        for connection_id in self._connections.keys():
            if except_of and connection_id in except_of:
                continue
            ops.append(self.push(event=event, connection_id=connection_id))
        await asyncio.gather(*ops)

    async def refresh_connection(self, connection_id: str):
        self._connections[connection_id].timeout_task.cancel()
        self._connections[connection_id].timeout_task = self._create_timeout_task(connection_id)
