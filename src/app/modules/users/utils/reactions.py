from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Reaction(Base):
    __tablename__ = "reaction"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    artworks_id: Mapped[int] = mapped_column(ForeignKey("artworks.id"), primary_key=True)
