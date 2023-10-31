from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class ArtworkImage(Base):
    __tablename__ = "artwork_images"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String)
    thumbnail_url = Column(String)  # URL миниатюры
    # is_thumbnail = Column(Boolean, default=False)

    # Отношение к объекту Artwork
    artwork_id = Column(Integer, ForeignKey("artworks.id"))
    artwork = relationship("Artwork", back_populates="images")

    # # Отношение к объекту ArtworkAdditions, через который можно будет обратиться напрямуюк Artwork
    # additions_id = Column(Integer, ForeignKey("artwork_additions.id"))
    # additions = relationship("ArtworkAdditions", back_populates="images")

    def create_thumbnail(self, thumbnail_image_url):
        # Позже добавить логику создания миниатюры из исходного изображения
        self.thumbnail_url = thumbnail_image_url
