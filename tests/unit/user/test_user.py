import jwt
import pytest
from pydantic import SecretStr

from src.domain.user.dtos import CreateUserDTO, LoginUserDTO, UserDTO
from src.domain.user.errors import (
    InvalidPasswordError,
    UserAlreadyExistsError,
    UserDoesNotExistError,
)
from src.domain.user.user import User
from src.settings import settings


@pytest.mark.anyio
async def test_create_user_success(user_aggregate: User):
    dto = CreateUserDTO(username="alice", password=SecretStr("p@ss"))
    created = await user_aggregate.create(dto)

    assert isinstance(created, UserDTO)
    assert created.username == "alice"
    # Ensure the password is stored as a hash (should not equal the raw password)
    assert created.password_hash.get_secret_value() != dto.password.get_secret_value()


@pytest.mark.anyio
async def test_create_user_already_exists(user_aggregate: User):
    dto = CreateUserDTO(username="bob", password=SecretStr("pwd"))
    await user_aggregate.create(dto)

    with pytest.raises(UserAlreadyExistsError):
        await user_aggregate.create(dto)


@pytest.mark.anyio
async def test_login_success_returns_valid_jwt(user_aggregate: User):
    username = "carol"
    password = SecretStr("secret")
    await user_aggregate.create(CreateUserDTO(username=username, password=password))

    token = await user_aggregate.login(LoginUserDTO(username=username, password=password))

    assert isinstance(token, str)
    payload = jwt.decode(
        token,
        settings.AUTH_SECRET_KEY.get_secret_value(),
        algorithms=[settings.AUTH_HASH_ALGORITHM],
    )
    assert payload[settings.AUTH_ACCESS_TOKEN_USERNAME_FIELD] == username


@pytest.mark.anyio
async def test_login_user_not_found(user_aggregate: User):
    with pytest.raises(UserDoesNotExistError):
        await user_aggregate.login(LoginUserDTO(username="nobody", password=SecretStr("x")))


@pytest.mark.anyio
async def test_login_invalid_password(user_aggregate: User):
    username = "dave"
    await user_aggregate.create(CreateUserDTO(username=username, password=SecretStr("right")))

    with pytest.raises(InvalidPasswordError):
        await user_aggregate.login(LoginUserDTO(username=username, password=SecretStr("wrong")))


@pytest.mark.anyio
async def test_get_current_valid_token_returns_user(user_aggregate: User):
    username = "erin"
    await user_aggregate.create(CreateUserDTO(username=username, password=SecretStr("pw")))

    token = await user_aggregate.login(LoginUserDTO(username=username, password=SecretStr("pw")))

    current = await user_aggregate.get_current(token)
    assert isinstance(current, UserDTO)
    assert current.username == username


@pytest.mark.anyio
async def test_get_current_invalid_or_unknown_user(user_aggregate: User):
    # Create a token for a user that doesn't exist in repo
    bogus_username = "ghost"
    data = {settings.AUTH_ACCESS_TOKEN_USERNAME_FIELD: bogus_username}
    token = jwt.encode(
        data,
        settings.AUTH_SECRET_KEY.get_secret_value(),
        algorithm=settings.AUTH_HASH_ALGORITHM,
    )

    with pytest.raises(UserDoesNotExistError):
        await user_aggregate.get_current(token)
