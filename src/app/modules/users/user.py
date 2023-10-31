from enum import StrEnum

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, declared_attr

from app.db import Base, get_async_session
from app.modules.users.roles import Role


# class UserRole(StrEnum):
#     witness = "witness"
#     artist = "artist"
#     moderator = "moderator"
#     admin = "admin"


class User(Base, SQLAlchemyBaseUserTable[int]):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(length=64), nullable=False)

    # @declared_attr
    # def role(cls):
    #     return mapped_column(Integer, ForeignKey(Role.id))


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
