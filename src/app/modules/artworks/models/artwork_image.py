from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

# from app.db import Base
from app.modules.cloud_storage.models import Image


class ArtworkImage(Image):
    __tablename__ = "artwork_image"
    id: Mapped[int] = mapped_column(None, ForeignKey("image.id"), primary_key=True)
    # __tablename__ = None
    # id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Отношение к объекту Artwork
    artwork_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("artwork.id", ondelete="CASCADE")
    )
    artwork: Mapped["Artwork"] = relationship("Artwork", back_populates="images")

    __mapper_args__ = {"polymorphic_identity": "artwork_image"}
