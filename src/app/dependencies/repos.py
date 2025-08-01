from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db import get_async_session
from src.infra.user.repos import UserRepository


async def user_repo_di(session: AsyncSession = Depends(get_async_session)) -> UserRepository:
    """Get the User repository as a dependency."""
    return UserRepository(session=session)
