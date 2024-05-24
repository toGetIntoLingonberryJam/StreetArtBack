import enum
from datetime import datetime
from enum import Enum as PyEnum

import pytz
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum

from app.db import Base


class ArtworkModerationStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ArtworkModeration(Base):
    __tablename__ = "artwork_moderation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    artwork_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("artwork.id", ondelete="CASCADE"), unique=True
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
