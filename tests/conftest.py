import asyncio

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.server import app as fastapi_app
from src.infra.db import AsyncSessionLocal, get_async_session


pytest_plugins = [
    "tests.fixtures",
]


@pytest.fixture
def app() -> FastAPI:
    """Create a test FastAPI app."""
    return fastapi_app


@pytest.fixture
async def test_client(app, test_db_session) -> AsyncClient:
    """Create a test client for the app."""

    # We pass session dependency as a fixture to assure that all the test scope will use the same DB session inside
    app.dependency_overrides[get_async_session] = lambda: test_db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def test_db_session():
    """
    Session for testing purposes.
    Assures that all the operations inside will be made in one transaction and will be rolled back.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.rollback()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()
