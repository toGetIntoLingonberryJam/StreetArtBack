from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

# from app.db import Base
from app.modules.images.models import Image
from app.modules.images.utils.classes import ImageModel


class ImageArtwork(Image):
    __tablename__ = ImageModel.IMAGE_ARTWORK.value
    __mapper_args__ = {"polymorphic_identity": ImageModel.IMAGE_ARTWORK.value}

    id: Mapped[int] = mapped_column(None, ForeignKey("image.id"), primary_key=True)

    # Отношение к объекту Artwork
    artwork_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("artwork.id", ondelete="CASCADE")
    )
    artwork: Mapped["Artwork"] = relationship("Artwork", back_populates="images")
