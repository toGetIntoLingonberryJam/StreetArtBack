import enum
from datetime import datetime

import pytz
from sqlalchemy import Integer, ForeignKey, DateTime, func, String, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.types import Enum

from app.db import Base
from app.modules.tickets.utils.classes import (
    TicketType,
    TicketStatus,
    TicketModel,
    TicketRegistry,
)


@TicketRegistry.register(TicketModel.TICKET)
class TicketBase(Base):
    __tablename__ = "ticket"

    __mapper_args__ = {
        "polymorphic_on": "discriminator",
        "polymorphic_identity": TicketModel.TICKET,
    }
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id = mapped_column(Integer, ForeignKey("user.id"), index=True)
    moderator_id = mapped_column(Integer, ForeignKey("moderator.id"), nullable=True)

    ticket_type = mapped_column(Enum(TicketType), nullable=False)
    reason = mapped_column(Text, nullable=True)

    status = mapped_column(Enum(TicketStatus), default=TicketStatus.PENDING)
    moderator_comment = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="tickets", lazy="selectin")
    moderator: Mapped["Moderator"] = relationship(
        back_populates="answered_tickets", lazy="selectin"
    )

    discriminator = mapped_column(String(50), nullable=False)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(tz=pytz.UTC),
        server_default=func.now(),
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(tz=pytz.UTC), onupdate=func.now()
    )

    # @declared_attr
    # def __tablename__(cls):
    #     return cls.__name__.lower()
    #
    # __mapper_args__ = {"polymorphic_identity": "base_ticket", "polymorphic_on": ticket_type}
