from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class ArtworkLocation(Base):
    __tablename__ = "artwork_location"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    address: Mapped[str] = mapped_column(String)

    # Поле, которое будет указывать на миниатюрное изображение в ImageArtwork
    thumbnail_image_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("image_artwork.id"), nullable=True
    )
    # Отношение к изображению ImageArtwork
    thumbnail_image = relationship(
        "ImageArtwork", foreign_keys=[thumbnail_image_id], lazy="selectin"
    )

    # Отношение "один-ко-одному" к объекту Artwork
    artwork_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("artwork.id", ondelete="CASCADE"), unique=True
    )
    artwork = relationship(
        "Artwork", back_populates="location", foreign_keys=[artwork_id]
    )
