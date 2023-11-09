from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.db import Base
from app.modules.users.user import User


class Role(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)

    user = relationship(User, backref="addresses")


class Witness(Role):
    __abstract__ = False
    __tablename__ = "witness"


class Artist(Role):
    __abstract__ = False
    __tablename__ = "artist"

    # works = relationship(Artwork)


class Moderator(Role):
    __abstract__ = False
    __tablename__ = "moderator"

    # requests = relationship(Req)


class Admin(Role):
    __abstract__ = False
    __tablename__ = "admin"

