from typing import List

from sqlalchemy import Integer, String, ARRAY, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Festival(Base):
    __tablename__ = "festival"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(length=70), index=True)
    description: Mapped[str] = mapped_column(String(length=320), nullable=True)
    artworks: Mapped[List["Artwork"]] = relationship(
        "Artwork", back_populates="festival", lazy="subquery"
    )
    image_id: Mapped[int] = mapped_column(ForeignKey("image.id"), nullable=True)
    image: Mapped["Image"] = relationship(lazy="joined",
                                          foreign_keys="Festival.image_id")

    links: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)

    likes: Mapped[List["User"]] = relationship(secondary="festival_like")
