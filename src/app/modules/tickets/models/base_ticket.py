import enum
from datetime import datetime

import pytz
from sqlalchemy import Integer, ForeignKey, DateTime, func, String, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.types import Enum

from app.db import Base


# Enum и базовая модель Ticket
class TicketType(str, enum.Enum):
    CREATE = "create"
    EDIT = "edit"
    COMPLAIN = "complain"


class TicketStatus(enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class TicketBase(Base):
    __tablename__ = "ticket"

    id = mapped_column(Integer, primary_key=True, index=True)
    user_id = mapped_column(Integer, ForeignKey("user.id"), index=True)
    ticket_type = mapped_column(Enum(TicketType), nullable=False)
    reason = mapped_column(Text, nullable=True)

    status = mapped_column(Enum(TicketStatus), default=TicketStatus.PENDING)
    moderator_comment = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="tickets")

    discriminator = mapped_column(String, nullable=False)
    __mapper_args__ = {"polymorphic_on": discriminator, "polymorphic_identity": "ticket"}

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
