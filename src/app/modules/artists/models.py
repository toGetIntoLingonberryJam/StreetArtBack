from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Artist(Base):
    __tablename__ = "artist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)

    # works = relationship(Artwork)

# get_current_artist = get_current_artist