import pytest

from src.domain.user import User
from src.infra.user.repos import UserRepository


@pytest.fixture
def user_aggregate(user_repository):
    return User(repo=user_repository)


@pytest.fixture
def user_repository(test_db_session):
    return UserRepository(test_db_session)