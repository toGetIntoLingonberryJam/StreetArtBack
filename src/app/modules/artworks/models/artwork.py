import enum
from datetime import datetime
from enum import Enum as PyEnum

import pytz
from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.types import Enum

from app.db import Base


class ArtworkStatus(str, PyEnum):
    EXISTING = "existing"
    DESTROYED = "destroyed"
    OVERPAINTED = "overpainted"


class Artwork(Base):
    __tablename__ = "artworks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)

    year_created: Mapped[int] = mapped_column(Integer)
    festival: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    source_description: Mapped[str] = mapped_column(String)

    # отношение к пользователю, который добавил арт-объект
    added_by_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    added_by_user = relationship(
        "User", back_populates="added_artworks", foreign_keys=[added_by_user_id]
    )

    # поля для связи арт-объекта с конкретным пользователем-художником, если он зарегистрирован
    artist_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=True
    )
    artist = relationship("User", back_populates="artwork", foreign_keys=[artist_id])

    # Отношение "один-ко-одному" к ArtworkLocation
    location = relationship(
        "ArtworkLocation",
        uselist=False,
        back_populates="artwork",
        foreign_keys="ArtworkLocation.artwork_id",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # Отношение "ОДИН-КО-МНОГИМ" к изображениям арт-объекта (ArtworkImage)
    images = relationship(
        "ArtworkImage",
        back_populates="artwork",
        foreign_keys="ArtworkImage.artwork_id",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    # поле для использования перечисления статуса объекта (ArtworkStatus)
    status: Mapped[enum] = mapped_column(
        Enum(ArtworkStatus), default=ArtworkStatus.EXISTING
    )

    # связь Artwork с ArtworkModeration
    moderation = relationship(
        "ArtworkModeration",
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

    def __repr__(self):
        return f"{self.title} (ID: {self.id})"
