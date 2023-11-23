from datetime import datetime
from enum import Enum as PyEnum

import pytz
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum

from app.db import Base

from app.modules.artworks.models.artwork_additions import ArtworkAdditions
from app.modules.artworks.models.artwork_location import ArtworkLocation
from app.modules.artworks.models.artwork_image import ArtworkImage
from app.modules.artworks.models.artwork_moderation import ArtworkModeration


class ArtworkStatus(str, PyEnum):
    EXISTING = "existing"
    DESTROYED = "destroyed"
    OVERPAINTED = "overpainted"


class Artwork(Base):
    __tablename__ = "artworks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)

    year_created = Column(Integer)
    festival = Column(String)
    description = Column(String)
    source_description = Column(String)

    # отношение к пользователю, который добавил арт-объект
    added_by_user_id = Column(Integer, ForeignKey("user.id"))
    added_by_user = relationship("User", back_populates="added_artworks", foreign_keys=[added_by_user_id])

    # поля для связи арт-объекта с конкретным пользователем-художником, если он зарегистрирован
    artist_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    artist = relationship("User", back_populates="artwork", foreign_keys=[artist_id])

    # Отношение "ОДИН-К-ОДНОМУ" (uselist=False) к дополнениям арт-объекта (ArtworkAdditions)
    # additions_id = Column(Integer, ForeignKey("artwork_additions.id"), nullable=True)
    additions = relationship("ArtworkAdditions", uselist=False, back_populates="artwork",
                             foreign_keys=[ArtworkAdditions.artwork_id],
                             cascade="all, delete-orphan")

    # Отношение "один-ко-одному" к ArtworkLocation
    # location_id = Column(Integer, ForeignKey("artwork_location.id"), nullable=True)
    location = relationship("ArtworkLocation", uselist=False, back_populates="artwork",
                            foreign_keys=[ArtworkLocation.artwork_id],
                            lazy="selectin",
                            cascade="all, delete-orphan")

    # Отношение "ОДИН-КО-МНОГИМ" к изображениям арт-объекта (ArtworkImage)
    images = relationship("ArtworkImage", back_populates="artwork",
                          foreign_keys=[ArtworkImage.artwork_id],
                          lazy="selectin",
                          cascade="all, delete-orphan")

    # поле для использования перечисления статуса объекта (ArtworkStatus)
    status = Column(Enum(ArtworkStatus), default=ArtworkStatus.EXISTING)

    # связь Artwork с ArtworkModeration
    moderation = relationship("ArtworkModeration", uselist=False, back_populates="artwork",
                              foreign_keys=[ArtworkModeration.artwork_id],
                              lazy="selectin",
                              cascade="all, delete-orphan")

    created_at = Column(DateTime(timezone=True), default=datetime.now(tz=pytz.UTC), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=datetime.now(tz=pytz.UTC), onupdate=func.now())

    # def get_image_urls(self):
    #     return [image.image_url for image in self.images]

    def __repr__(self):
        return f"{self.title} (ID: {self.id})"

