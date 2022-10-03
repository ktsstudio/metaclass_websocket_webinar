from dataclasses import asdict

from app.base.accessor import BaseManager
from app.store.ws.ws_accessor import Event


class GeoServerEventKind:
    INITIAL = 'initial'
    ADD = 'add'
    MOVE = 'move'
    REMOVE = 'remove'


class GeoClientEventKind:
    CONNECT = 'connect'
    DISCONNECT = 'disconnect'
    PING = 'ping'


class GeoManager(BaseManager):
    class Meta:
        name = 'geo_manager'

    MAX_ERROR = 0.05

    async def handle(self, connection_id: str):
        await self._send_initial_event(connection_id)
        async for event in self.store.ws_accessor.stream(connection_id):
            should_continue = await self._handle_event(event, connection_id)
            if not should_continue:
                break

    async def _handle_event(self, event: Event, connection_id: str) -> bool:
        if event.kind == GeoClientEventKind.CONNECT:
            user = await self.store.users_accessor.add(
                _id=connection_id,
                name=event.payload['name'],
                latitude=event.payload['latitude'],
                longitude=event.payload['longitude'],
            )
            self.logger.info(f'New user connected: {user}')
            payload = asdict(user)
            payload['id'] = connection_id
            event = Event(
                kind=GeoServerEventKind.ADD,
                payload=payload,
            )
            await self.store.ws_accessor.broadcast(
                event,
                except_of=[connection_id],
            )
            return True
        elif event.kind == GeoClientEventKind.DISCONNECT:
            user = await self.store.users_accessor.get(_id=connection_id)
            self.logger.info(f'User {user} disconnected')
            await self.on_user_disconnect(connection_id)
            return True
        elif event.kind == GeoClientEventKind.PING:
            user = await self.store.users_accessor.get(connection_id)
            latitude = event.payload['latitude']
            longitude = event.payload['longitude']

            if abs(user.latitude - latitude) > self.MAX_ERROR or abs(user.longitude - longitude) > self.MAX_ERROR:
                await self.store.ws_accessor.broadcast(
                    event=Event(
                        kind=GeoServerEventKind.MOVE,
                        payload={
                            'id': user.id,
                            'latitude': latitude,
                            'longitude': longitude,
                        }
                    ),
                    except_of=[connection_id],
                )
                await self.store.users_accessor.update_coords(
                    _id=user.id,
                    latitude=latitude,
                    longitude=longitude,
                )
            return True
        else:
            raise NotImplementedError

    async def _send_initial_event(self, connection_id: str):
        event = Event(
            kind=GeoServerEventKind.INITIAL,
            payload={
                'users': [asdict(user) for user in await self.store.users_accessor.list_users()]
            },
        )
        await self.store.ws_accessor.push(event, connection_id=connection_id)

    async def on_user_disconnect(self, connection_id: str) -> None:
        await self.store.users_accessor.remove(connection_id)
        await self.store.ws_accessor.broadcast(
            event=Event(
                kind=GeoServerEventKind.REMOVE,
                payload={
                    'id': connection_id,
                },
            ),
            except_of=[connection_id],
        )
