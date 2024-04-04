from typing import List

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Moderator(Base):
    __tablename__ = "moderator"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)

    answered_tickets: Mapped[List["TicketBase"]] = relationship(
        back_populates="moderator"
    )

    # requests = relationship(Req)
