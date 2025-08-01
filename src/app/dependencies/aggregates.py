from fastapi import Depends

from src.app.dependencies.repos import user_repo_di
from src.domain.user import IUserRepo, User


async def user_aggregate_di(repo: IUserRepo = Depends(user_repo_di)) -> User:
    """Get the User aggregate as a dependency."""
    return User(repo=repo)
