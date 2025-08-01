from pydantic import BaseModel, SecretStr


class RegistrationRequest(BaseModel):
    username: str
    password: SecretStr


class RegistrationResponse(BaseModel):
    username: str


class LoginRequest(BaseModel):
    username: str
    password: SecretStr


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


class CurrentUserResponse(BaseModel):
    username: str
