from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infra.db import DBBaseModel


class UserModel(DBBaseModel):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, primary_key=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
