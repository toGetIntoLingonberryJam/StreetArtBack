from enum import StrEnum

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase

from sqlalchemy import Integer, String, Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, get_async_session
from app.modules.artworks.models.artwork import Artwork


class UserRole(StrEnum):
    witness = "witness"
    artist = "artist"
    moderator = "moderator"
    admin = "admin"


class User(Base, SQLAlchemyBaseUserTable[int]):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(length=64), nullable=False)
      
    # отношение к добавленным арт-объектам
    added_artworks = relationship("Artwork", back_populates="added_by_user", foreign_keys=[Artwork.added_by_user_id])
    artwork = relationship("Artwork", back_populates="artist", foreign_keys=[Artwork.artist_id])

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.witness)


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
