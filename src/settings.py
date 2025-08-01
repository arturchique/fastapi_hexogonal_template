from typing import Any, cast

from pydantic import PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App settings
    DEBUG: bool = True

    # DB
    POSTGRES_SERVER: str = "db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "teacher"
    POSTGRES_PORT: str = "5432"
    DATABASE_URI: PostgresDsn | None = None

    @field_validator("DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: Any) -> Any:
        if isinstance(v, str):
            return v

        values = cast(dict[str, Any], info.data)
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=int(values.get("POSTGRES_PORT", "5432")),
            path=f"{values.get('POSTGRES_DB') or ''}",
        )

    # Auth
    AUTH_SECRET_KEY: SecretStr
    AUTH_PASSWORD_SALT: SecretStr
    AUTH_HASH_ALGORITHM: str = "HS256"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    AUTH_ACCESS_TOKEN_USERNAME_FIELD: str = "sub"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
