from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.app.auth import schemas
from src.app.dependencies.aggregates import user_aggregate_di
from src.app.dependencies.auth import current_user_di
from src.domain.user import CreateUserDTO, InvalidPasswordError, LoginUserDTO, User, UserAlreadyExistsError, UserDTO


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register_user(
    user_data: schemas.RegistrationRequest,
    user_aggregate: User = Depends(user_aggregate_di),
) -> schemas.RegistrationResponse:
    try:
        user = await user_aggregate.create(CreateUserDTO(username=user_data.username, password=user_data.password))
        return schemas.RegistrationResponse(
            username=user.username,
        )
    except UserAlreadyExistsError:
        raise HTTPException(status_code=400, detail="User with this username already exists.")


@router.post("/login")
async def oauth2_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_aggregate: User = Depends(user_aggregate_di),
) -> schemas.LoginResponse:
    """Neededd for OAUTH2 login."""

    try:
        token = await user_aggregate.login(LoginUserDTO(username=form_data.username, password=form_data.password))
        return schemas.LoginResponse(access_token=token, token_type="bearer")
    except UserAlreadyExistsError:
        raise HTTPException(status_code=400, detail="User with this username does not exist.")
    except InvalidPasswordError:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/login-json")
async def json_login(
    login_data: schemas.LoginRequest,
    user_aggregate: User = Depends(user_aggregate_di),
) -> schemas.LoginResponse:
    """Needed for registration by credentials in JSON format."""

    try:
        token = await user_aggregate.login(LoginUserDTO(username=login_data.username, password=login_data.password))
        return schemas.LoginResponse(access_token=token, token_type="bearer")
    except UserAlreadyExistsError:
        raise HTTPException(status_code=400, detail="User with this username does not exist.")
    except InvalidPasswordError:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me")
async def get_current_user(
    current_user: UserDTO = Depends(current_user_di),
) -> schemas.CurrentUserResponse:
    return schemas.CurrentUserResponse(
        username=current_user.username,
    )
