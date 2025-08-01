import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.settings import settings


logger = logging.getLogger(__name__)


class DBBaseModel(DeclarativeBase):
    """Base class for SQLAlchemy models."""


# Asynchronous engine and session factory
async_engine = create_async_engine(
    str(settings.DATABASE_URI),
    echo=settings.DEBUG,
)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a database session for asynchronous operations.
    Assures that all the operations inside will be made in one transaction.

    IMPORTANT!!!
    Avoid using session.commit() inside one session.
    If you need to persist data inside transaction -- use session.flush()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
