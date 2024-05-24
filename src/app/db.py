from typing import AsyncGenerator

from redis import asyncio as aioredis
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from config import settings

redis = aioredis.from_url(str(settings.redis_url), decode_responses=True)

metadata = MetaData()
Base = declarative_base(metadata=metadata)


engine = create_async_engine(str(settings.database_url))
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
