from typing import List

from fastapi import Depends, HTTPException
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.modules.users.fastapi_users_config import current_user
from app.modules.users.models import User


class Moderator(Base):
    __tablename__ = "moderator"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)

    answered_tickets: Mapped[List["TicketBase"]] = relationship(
        back_populates="moderator"
    )

    # requests = relationship(Req)
