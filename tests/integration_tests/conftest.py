import asyncio
from typing import AsyncGenerator

import pytest_asyncio
from fastapi.testclient import TestClient
from asgi_lifespan import LifespanManager

import pytest
from httpx import AsyncClient

from app.app import app

# SETUP


@pytest.fixture(scope="session")
def sync_client() -> TestClient:
    with TestClient(app) as sync_client:
        yield sync_client


@pytest_asyncio.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as async_client:
            yield async_client
