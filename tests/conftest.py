import asyncio
from typing import AsyncGenerator

import pytest
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from app.app import app
from app.db import Base, get_async_session, redis

from redis.exceptions import ConnectionError
from config import settings

engine_test = create_async_engine(str(settings.database_url), poolclass=NullPool)
async_session_maker = async_sessionmaker(engine_test, expire_on_commit=False)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session  # noqa


@pytest.fixture(scope="session")
async def test_redis(request):
    try:
        # Проверка подключения к Redis. Иначе - краш.
        await redis.ping()
    except ConnectionError as e:
        pytest.skip(
            "Ошибка при проверке подключения к Redis. Интеграционные тесты отключены"
        )


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    assert settings.mode == "TEST"
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Создание всех таблиц в БД
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Удаление всех таблиц в БД


@pytest.fixture(scope="function")
async def clear_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


# SETUP


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
