from dataclasses import dataclass, asdict

from app.base.accessor import BaseAccessor
from app.store.geo.events import ClientEventKind, ServerEventKind
from app.store.ws.ws_accessor import Event


@dataclass
class User:
    id: str
    latitude: float
    longitude: float
    name: str


class GeoManager(BaseAccessor):
    class Meta:
        name = 'geo'

    def _init_(self) -> None:
        self._users: dict[str, User] = {}

    async def handle_event(self, event: dict):
        kind = event['kind']
        data = event['data']
        user_id = data['id']
        self.logger.info(f'New event with kind {kind} and payload {data}')
        if kind == ClientEventKind.CONNECT:
            await self._on_connect(user_id, data)
        elif kind == ClientEventKind.DISCONNECT:
            await self._on_disconnect(user_id)
        elif kind == ClientEventKind.PING:
            await self._on_ping(user_id, data['latitude'], data['longitude'])
        else:
            raise NotImplementedError(kind)

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

    async def _on_connect(self, user_id, data: dict):
        latitude, longitude = data['latitude'], data['longitude']
        name = data['name']
        try:
            self._users.pop(user_id)
        except KeyError:
            pass
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
        self._users.pop(user_id)
        await self.store.ws.push_all(Event(
            kind=ServerEventKind.REMOVE,
            payload={
                'id': user_id,
            }
        ), except_of=[user_id])

    async def _on_ping(self, user_id, latitude, longitude):
        user = self._users[user_id]

        if user.latitude - latitude > 0.05 or user.longitude - longitude > 0.05:
            await self.store.ws.push_all(Event(
                kind=ServerEventKind.MOVE,
                payload=asdict(user),
            ), except_of=[user_id])

        user.latitude = latitude
        user.longitude = longitude
