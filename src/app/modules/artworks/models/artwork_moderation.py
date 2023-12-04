import enum
from datetime import datetime

import pytz
from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db import Base
from enum import Enum as PyEnum
from sqlalchemy.types import Enum


class ArtworkModerationStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ArtworkModeration(Base):
    __tablename__ = "artwork_moderation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    artwork_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("artworks.id", ondelete="CASCADE"), unique=True
    )
    status: Mapped[enum] = mapped_column(
        Enum(ArtworkModerationStatus), default=ArtworkModerationStatus.PENDING
    )
    comment: Mapped[str] = mapped_column(String, nullable=True)

    # определение отношения ArtworkModeration к Artwork
    artwork = relationship("Artwork", back_populates="moderation")

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(tz=pytz.UTC), onupdate=func.now()
    )
