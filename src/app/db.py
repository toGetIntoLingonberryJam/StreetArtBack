import asyncio
from typing import AsyncGenerator

from fastapi import HTTPException
from sqlalchemy import MetaData
from sqlalchemy.exc import StatementError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from config import DATABASE_URL

metadata = MetaData()
Base = declarative_base(metadata=metadata)

engine = create_async_engine(DATABASE_URL,
                             pool_pre_ping=True,  # Проверять соединение перед выполнением запроса
                             pool_recycle=3600)   # Пересоздавать соединение каждый час)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
#     async with async_session_maker() as session:
#         yield session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    max_retries = 3  # Максимальное количество попыток создания сессии
    retry_count = 0

    while retry_count < max_retries:
        try:
            print("retry_count: " + str(retry_count))  # ToDO: убрать
            async with async_session_maker() as session:
                return session
        except StatementError as e:
            print(f"Ошибка при получении сессии: {e}")
            retry_count += 1
            await asyncio.sleep(1)  # Можно установить другую задержку перед повторной попыткой

    raise HTTPException(status_code=500, detail="Не удалось создать сессию после нескольких попыток")

