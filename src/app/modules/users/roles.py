from sqlalchemy import Integer
from sqlalchemy.orm import mapped_column, Mapped

from app.db import Base


class Role(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

#
# class Witness(Role):
#     __tablename__ = "witness"
#
#
# class Artist(Role):
#     __tablename__ = "artist"
#
#
# class Moderator(Role):
#     __tablename__ = "moderator"
#
#
# class Admin(Role):
#     __tablename__ = "admin"

