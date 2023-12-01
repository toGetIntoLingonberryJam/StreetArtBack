from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.modules.artworks.models.artwork import Artwork


class Artist(Base):
    __tablename__ = "artist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)

    artwork = relationship("Artwork", back_populates="artist", foreign_keys=[Artwork.artist_id])

# get_current_artist = get_current_artist

