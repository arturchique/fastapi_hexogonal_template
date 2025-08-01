from pydantic import BaseModel, SecretStr


class CreateUserDTO(BaseModel):
    username: str
    password: SecretStr


class LoginUserDTO(BaseModel):
    username: str
    password: SecretStr


class UserDTO(BaseModel):
    username: str
    password_hash: SecretStr
