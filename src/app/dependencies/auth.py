from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from src.app.dependencies.aggregates import user_aggregate_di
from src.domain.user import User, UserDoesNotExistError, UserDTO


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def current_user_di(
    token: str = Depends(oauth2_scheme),
    user_aggregate: User = Depends(user_aggregate_di),
) -> UserDTO:
    """Get the current user as a dependency."""
    try:
        print("token:", token)
        return await user_aggregate.get_current(token)
    except UserDoesNotExistError:
        raise HTTPException(status_code=401, detail="User is not authenticated.")
