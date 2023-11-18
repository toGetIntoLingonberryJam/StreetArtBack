from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class ArtworkAdditions(Base):
    __tablename__ = "artwork_additions"

    id = Column(Integer, primary_key=True, index=True)
    # artwork_id = Column(Integer, ForeignKey("artworks.id"))

    # Отношение к арт-объекту (Artwork)
    artwork_id = Column(Integer, ForeignKey("artworks.id", ondelete="CASCADE"))
    artwork = relationship(
        "Artwork", back_populates="additions", foreign_keys=[artwork_id]
    )

    # Отношение к изображениям арт-объекта (ArtworkImage)
    # images = relationship("ArtworkImage", back_populates="additions")
