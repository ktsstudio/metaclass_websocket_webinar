import asyncio
import uuid
from asyncio import Task
from dataclasses import dataclass, asdict

from app.base.accessor import BaseAccessor
from app.store.geo.events import ClientEventKind, ServerEventKind
from app.store.ws.ws_accessor import Event


@dataclass
class User:
    id: str
    name: str
    latitude: float
    longitude: float


class GeoManager(BaseAccessor):
    class Meta:
        name = 'geo'

    def _init_(self) -> None:
        self._users: dict[str, User] = {}
        self._close_tasks: dict[str, Task] = {}

    async def handle_event(self, event: Event):
        user_id = event.payload['id']  # по нашему протоколу клиент всегда присылает поле id
        if event.kind == ClientEventKind.CONNECT:
            await self._on_connect(user_id, event.payload)
        elif event.kind == ClientEventKind.DISCONNECT:
            await self._on_disconnect(user_id)
        elif event.kind == ClientEventKind.PING:
            await self._on_ping(user_id, event.payload['latitude'], event.payload['longitude'])
        else:
            raise NotImplementedError(event.kind)

    async def handle_open(self, user_id: str):
        await self.store.ws.push(
            user_id,
            event=Event(
                kind=ServerEventKind.INITIAL,
                payload={
                    'id': str(user_id),
                    'users': [asdict(_user) for _user in self._users.values()],
                },
            ),
        )

    async def handle_close(self, user_id: str):
        await self._on_disconnect(user_id)

    async def _on_connect(self, user_id: str, payload: dict):
        latitude, longitude, name = payload['latitude'], payload['longitude'], payload['name']
        self.logger.info(f'{name} joined! {latitude=}, {longitude=}')
        self._users[user_id] = User(
            id=user_id,
            name=name,
            latitude=latitude,
            longitude=longitude,
        )
        await self.store.ws.push_all(Event(
            kind=ServerEventKind.ADD,
            payload=asdict(self._users[user_id]),
        ), except_of=[user_id])

    async def _on_disconnect(self, user_id: str):
        user = self._users.pop(user_id)
        self.logger.info(f'{user.name} left, bye bye!')
        await self.store.ws.push_all(Event(
            kind=ServerEventKind.REMOVE,
            payload={
                'id': user_id,
            }
        ), except_of=[user_id])

    async def _on_ping(self, user_id: str, latitude: float, longitude: float):
        user = self._users[user_id]
        self.logger.info(f'ping from {user.name}')

        if abs(user.latitude - latitude) > 0.05 or abs(user.longitude - longitude) > 0.05:
            self.logger.info(f'{user.name} moved!')
            user.latitude, user.longitude = latitude, longitude
            await self.store.ws.push_all(Event(
                kind=ServerEventKind.MOVE,
                payload=asdict(user),
            ), except_of=[user_id])
        else:
            user.latitude, user.longitude = latitude, longitude
