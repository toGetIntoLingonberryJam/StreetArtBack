from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Authorship(Base):
    __tablename__ = "authorship"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"), index=True)
    artwork_id: Mapped[int] = mapped_column(ForeignKey("artwork.id"), index=True)
