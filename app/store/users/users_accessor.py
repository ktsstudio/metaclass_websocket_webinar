from dataclasses import dataclass

from app.base.accessor import BaseAccessor


@dataclass
class User:
    id: str
    name: str
    latitude: float
    longitude: float

    def __str__(self):
        return f'User {self.name} ({self.id}: latitude {self.latitude}, longitude: {self.longitude}'


class UsersAccessor(BaseAccessor):
    def _init_(self) -> None:
        self._users: dict[str, User] = {}

    async def list_users(self) -> list[User]:
        return list(self._users.values())

    async def update_coords(
            self,
            _id: str,
            latitude: float,
            longitude: float,
    ):
        self._users[_id].latitude = latitude
        self._users[_id].longitude = longitude

    async def add(
            self,
            _id: str,
            name: str,
            latitude: float,
            longitude: float,
    ) -> User:
        user = User(
            id=_id,
            name=name,
            latitude=latitude,
            longitude=longitude,
        )
        self._users[_id] = user
        return user

    async def remove(self, _id: str) -> None:
        self._users.pop(_id)

    async def get(self, _id: str) -> User:
        return self._users[_id]
