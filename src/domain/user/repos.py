from typing import Protocol

from src.domain.user.dtos import UserDTO


class IUserRepo(Protocol):
    async def create(self, user: UserDTO) -> UserDTO:
        raise NotImplementedError

    async def find_by_username(self, username: str) -> UserDTO | None:
        raise NotImplementedError
