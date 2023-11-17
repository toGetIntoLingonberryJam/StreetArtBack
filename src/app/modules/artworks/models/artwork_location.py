from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class ArtworkLocation(Base):
    __tablename__ = "artwork_location"

    id = Column(Integer, primary_key=True, index=True)

    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String)

    # Поле, которое будет указывать на миниатюрное изображение в ArtworkImage
    thumbnail_image_id = Column(Integer, ForeignKey("artwork_images.id"), nullable=True)
    # Отношение к изображению ArtworkImage
    thumbnail_image = relationship(
        "ArtworkImage", foreign_keys=[thumbnail_image_id], lazy="selectin"
    )

    # Отношение "один-ко-одному" к объекту Artwork
    artwork_id = Column(
        Integer, ForeignKey("artworks.id", ondelete="CASCADE"), unique=True
    )
    artwork = relationship(
        "Artwork", back_populates="location", foreign_keys=[artwork_id]
    )
