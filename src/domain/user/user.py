from datetime import timedelta, datetime, UTC
from hashlib import sha256

import jwt
from pydantic import SecretStr

from src.domain.user.dtos import CreateUserDTO, LoginUserDTO, UserDTO
from src.domain.user.errors import InvalidPasswordError, UserAlreadyExistsError, UserDoesNotExistError
from src.domain.user.repos import IUserRepo
from src.settings import settings


class User:
    def __init__(self, repo: IUserRepo):
        self._repo = repo

    async def create(self, create_data: CreateUserDTO) -> UserDTO:
        existed_user = await self.find_by_username(create_data.username)
        if existed_user:
            raise UserAlreadyExistsError("User with this username already exists.")

        password_hash = self._get_password_hash(create_data.password)
        return await self._repo.create(UserDTO(username=create_data.username, password_hash=password_hash))

    async def login(self, login_data: LoginUserDTO) -> str:
        user = await self.find_by_username(login_data.username)
        if not user:
            raise UserDoesNotExistError("User with this username does not exist.")
        if not self._verify_password(login_data.password, user.password_hash):
            raise InvalidPasswordError

        return self._create_access_token(login_data.username)

    async def find_by_username(self, username: str) -> UserDTO | None:
        return await self._repo.find_by_username(username)

    async def get_current(self, token: str) -> UserDTO:
        try:
            print("********\n" * 10)
            print(token)
            payload = jwt.decode(
                token,
                settings.AUTH_SECRET_KEY.get_secret_value(),
                algorithms=[settings.AUTH_HASH_ALGORITHM],
            )
            username = payload.get(settings.AUTH_ACCESS_TOKEN_USERNAME_FIELD)
            if not username:
                raise UserDoesNotExistError("Invalid token payload.")

            user = await self.find_by_username(username)
            if user is None:
                raise UserDoesNotExistError("User with this username does not exist.")
            return user
        except jwt.InvalidTokenError as e:
            print(e)
            raise UserDoesNotExistError("Invalid token payload.")

    def _verify_password(self, password_to_check: SecretStr, actual_password_hash: SecretStr) -> bool:
        """Verify if the provided password matches the stored hash."""
        password_hash_to_check = self._get_password_hash(password_to_check)
        return password_hash_to_check == actual_password_hash.get_secret_value()

    @staticmethod
    def _get_password_hash(password: SecretStr) -> str:
        """Generate a hashed password."""
        pwd_bytes = password.get_secret_value().encode()
        salt = settings.AUTH_PASSWORD_SALT.get_secret_value().encode()

        hasher = sha256()
        hasher.update(pwd_bytes + salt)
        return hasher.hexdigest()

    @staticmethod
    def _create_access_token(username: str) -> str:
        access_token_expires_delta = timedelta(minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {
            settings.AUTH_ACCESS_TOKEN_USERNAME_FIELD: username,
            "exp": datetime.now(UTC) + access_token_expires_delta,
        }
        return jwt.encode(
            data,
            settings.AUTH_SECRET_KEY.get_secret_value(),
            algorithm=settings.AUTH_HASH_ALGORITHM,
        )
