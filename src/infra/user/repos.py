from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.user import UserAlreadyExistsError, UserDoesNotExistError, UserDTO
from src.infra.base_repository import BaseRepository
from src.infra.user.models import UserModel


class UserRepository(BaseRepository[UserModel, UserDTO, str]):
    def __init__(self, session: AsyncSession):
        super().__init__(
            session=session,
            model_class=UserModel,
            id_field="username",
            already_exists_exception_class=UserAlreadyExistsError,
            not_found_exception_class=UserDoesNotExistError,
        )

    async def find_by_username(self, username: str) -> UserDTO | None:
        return await self.get_by_id(entity_id=username)

    def map_dto_to_model(self, dto: UserDTO) -> UserModel:
        return UserModel(username=dto.username, password_hash=dto.password_hash.get_secret_value())

    def map_model_to_dto(self, model: UserModel) -> UserDTO:
        return UserDTO(username=model.username, password_hash=model.password_hash)
