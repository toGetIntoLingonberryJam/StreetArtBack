from datetime import datetime
import pytz

from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db import Base


class ArtworkImage(Base):
    __tablename__ = "artwork_image"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    image_url: Mapped[str] = mapped_column(String, unique=True)

    # Отношение к объекту Artwork
    artwork_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("artwork.id", ondelete="CASCADE")
    )
    artwork = relationship("Artwork", back_populates="images")

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(tz=pytz.UTC),
        server_default=func.now(),
    )
