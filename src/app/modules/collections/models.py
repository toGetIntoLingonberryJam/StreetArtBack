import enum

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class LikeType(enum.Enum):
    ARTWORK = "artwork"
    FESTIVAL = "festival"
    ARTIST = "artist"


class ArtworkLike(Base):
    __tablename__ = "artwork_like"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    artwork_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("artwork.id"), index=True, nullable=True
    )


class FestivalLike(Base):
    __tablename__ = "festival_like"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    festival_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("festival.id"), index=True, nullable=True
    )


class ArtistLike(Base):
    __tablename__ = "artist_like"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    artist_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("artist.id"), index=True, nullable=True
    )
