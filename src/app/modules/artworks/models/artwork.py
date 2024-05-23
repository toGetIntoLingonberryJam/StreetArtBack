import enum
from datetime import datetime
from enum import Enum as PyEnum
from typing import List

import pytz
from sqlalchemy import ARRAY, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum

from app.db import Base


class ArtworkStatus(str, PyEnum):
    EXISTING = "existing"
    DESTROYED = "destroyed"
    OVERPAINTED = "overpainted"


class Artwork(Base):
    __tablename__ = "artwork"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)

    year_created: Mapped[int] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    # source_description: Mapped[str] = mapped_column(String, nullable=True)
    links: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)

    # отношение к пользователю, который добавил арт-объект
    added_by_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    added_by_user: Mapped["User"] = relationship(
        back_populates="added_artworks", foreign_keys=[added_by_user_id]
    )

    # поля для связи арт-объекта с конкретным пользователем-художником, если он зарегистрирован
    artist_id = mapped_column(ForeignKey("artist.id"), nullable=True)
    artist: Mapped["Artist"] = relationship(
        "Artist", foreign_keys=artist_id, back_populates="artworks", lazy="joined"
    )

    festival_id: Mapped[int] = mapped_column(ForeignKey("festival.id"), nullable=True)
    festival: Mapped["Festival"] = relationship(
        "Festival", foreign_keys=festival_id, back_populates="artworks", lazy="joined"
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("artwork_location.id", use_alter=True), nullable=True
    )
    # Отношение "один-ко-одному" к ArtworkLocation
    location: Mapped["ArtworkLocation"] = relationship(
        uselist=False,
        back_populates="artwork",
        foreign_keys="ArtworkLocation.artwork_id",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # Отношение "ОДИН-КО-МНОГИМ" к изображениям арт-объекта (ImageArtwork)
    images: Mapped[List["ImageArtwork"]] = relationship(
        back_populates="artwork",
        foreign_keys="ImageArtwork.artwork_id",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # поле для использования перечисления статуса объекта (ArtworkStatus)
    status: Mapped[enum] = mapped_column(
        Enum(ArtworkStatus), default=ArtworkStatus.EXISTING
    )

    # связь Artwork с ArtworkModeration
    moderation: Mapped["ArtworkModeration"] = relationship(
        uselist=False,
        back_populates="artwork",
        foreign_keys="ArtworkModeration.artwork_id",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(tz=pytz.UTC),
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(tz=pytz.UTC), onupdate=func.now()
    )

    likes: Mapped[List["User"]] = relationship(secondary="artwork_like", lazy="selectin")

    def __repr__(self):
        return f"{self.title} (ID: {self.id})"
