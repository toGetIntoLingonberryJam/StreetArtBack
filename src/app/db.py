from typing import AsyncGenerator
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from config import get_settings
from redis import asyncio as aioredis

redis = aioredis.from_url(str(get_settings().redis_url), decode_responses=True)


metadata = MetaData()
Base = declarative_base(metadata=metadata)

engine = create_async_engine(
    str(get_settings().database_url),
    pool_pre_ping=True,  # Проверять соединение перед выполнением запроса
    pool_recycle=3600,  # Пересоздавать соединение каждый час
)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
