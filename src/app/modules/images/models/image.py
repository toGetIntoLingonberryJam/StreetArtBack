from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.modules.images.utils.classes import ImageModel


class Image(Base):
    __tablename__ = ImageModel.IMAGE.value

    __mapper_args__ = {
        "polymorphic_on": "discriminator",
        "polymorphic_identity": ImageModel.IMAGE.value,
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    image_url: Mapped[str] = mapped_column(String)
    public_key: Mapped[str] = mapped_column(String)
    file_path: Mapped[str] = mapped_column(String)

    blurhash: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String(length=50), nullable=True)

    discriminator = mapped_column(String(50), nullable=False)
