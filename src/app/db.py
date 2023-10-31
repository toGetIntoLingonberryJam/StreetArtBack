from typing import AsyncGenerator
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from config import DATABASE_URL

metadata = MetaData()
Base = declarative_base(metadata=metadata)

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    # TODO: Что-то надо с этим делать... (Черновой вариант)
    #  Вероятно, если мы используем модульную систему хранения логики, где модели хранятся внутри пакета модуля, то нам
    #  стоит создать некую функцию import_models(), где будет реализован импорт всех модулей (artwork, users, map...) и уже
    #  автоматически будет находить модели модулей и импортировать, юзая importlib.
    #  Представляю это как некое подобие модулей в Django.
    from app.modules.artworks.models.artwork_additions import ArtworkAdditions  # noqa
    from app.modules.artworks.models.artwork_image import ArtworkImage  # noqa
    from app.modules.artworks.models.artwork_location import ArtworkLocation  # noqa
    from app.modules.artworks.models.artwork import Artwork  # noqa
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
