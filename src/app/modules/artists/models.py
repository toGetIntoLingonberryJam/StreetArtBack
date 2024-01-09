from typing import List

from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Artist(Base):
    __tablename__ = "artist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # псевдоним артиста
    name: Mapped[str] = mapped_column(String(length=50), index=True)
    description: Mapped[str] = mapped_column(String(length=320), nullable=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), index=True, nullable=True
    )
    artworks: Mapped[List["Artwork"]] = relationship(
        "Artwork", back_populates="artist", lazy="subquery"
    )

    links: Mapped[List[str]] = mapped_column(ARRAY(String))
