from datetime import datetime
import pytz

from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class Image(Base):
    __tablename__ = "image"

    __mapper_args__ = {
        "polymorphic_on": "discriminator",
        "polymorphic_identity": "image",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    image_url: Mapped[str] = mapped_column(String)
    public_key: Mapped[str] = mapped_column(String)
    file_path: Mapped[str] = mapped_column(String)

    description: Mapped[str] = mapped_column(String(length=50), nullable=True)

    discriminator = mapped_column(String(50), nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(tz=pytz.UTC),
        server_default=func.now(),
    )
