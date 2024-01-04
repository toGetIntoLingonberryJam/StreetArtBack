from typing import List

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase

from sqlalchemy import Integer, String, Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, get_async_session
from app.modules.artists.models import Artist
from app.modules.artworks.models.artwork import Artwork
from app.modules.users.utils.reactions import Reaction



class User(Base, SQLAlchemyBaseUserTable[int]):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(length=64), nullable=False)

    # отношение к добавленным арт-объектам
    added_artworks = relationship("Artwork", back_populates="added_by_user", foreign_keys=[Artwork.added_by_user_id])

    # отношение MANY-TO-MANY к любимым работам
    favorite_artworks: Mapped[List["Artwork"]] = relationship("Artwork", secondary="reaction")

    is_artist: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_moderator: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
