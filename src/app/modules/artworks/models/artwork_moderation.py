from datetime import datetime

import pytz
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db import Base
from enum import Enum as PyEnum
from sqlalchemy.types import Enum


class ArtworkModerationStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ArtworkModeration(Base):
    __tablename__ = "artwork_moderation"

    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(
        Integer, ForeignKey("artworks.id", ondelete="CASCADE"), unique=True
    )
    status = Column(
        Enum(ArtworkModerationStatus), default=ArtworkModerationStatus.PENDING
    )
    comment = Column(String, nullable=True)

    # определение отношения ArtworkModeration к Artwork
    artwork = relationship("Artwork", back_populates="moderation")

    updated_at = Column(
        DateTime(timezone=True), default=datetime.now(tz=pytz.UTC), onupdate=func.now()
    )
