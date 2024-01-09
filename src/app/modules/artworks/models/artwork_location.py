from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db import Base


class ArtworkLocation(Base):
    __tablename__ = "artwork_location"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    address: Mapped[str] = mapped_column(String)

    # Поле, которое будет указывать на миниатюрное изображение в ArtworkImage
    thumbnail_image_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("artwork_image.id"), nullable=True
    )
    # Отношение к изображению ArtworkImage
    thumbnail_image = relationship(
        "ArtworkImage", foreign_keys=[thumbnail_image_id], lazy="selectin"
    )

    # Отношение "один-ко-одному" к объекту Artwork
    artwork_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("artwork.id", ondelete="CASCADE"), unique=True
    )
    artwork = relationship(
        "Artwork", back_populates="location", foreign_keys=[artwork_id]
    )
