from datetime import datetime
import pytz

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.db import Base


class ArtworkImage(Base):
    __tablename__ = "artwork_images"

    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, unique=True)

    # Отношение к объекту Artwork
    artwork_id = Column(Integer, ForeignKey("artworks.id", ondelete="CASCADE"))
    artwork = relationship("Artwork", back_populates="images")

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.now(tz=pytz.UTC),
        server_default=func.now(),
    )
