from datetime import datetime

import pytz
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum

from app.db import Base
from app.modules.tickets.utils.classes import (
    TicketAvailableObjectClasses,
    TicketModel,
    TicketRegistry,
    TicketStatus,
    TicketType,
)


@TicketRegistry.register(TicketModel.TICKET)
class TicketBase(Base):
    __tablename__ = TicketModel.TICKET.value

    __mapper_args__ = {
        "polymorphic_on": "discriminator",
        "polymorphic_identity": TicketModel.TICKET.value,
    }
    discriminator = mapped_column(String(50), nullable=False)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Для разграничения тикетов к объекту по классу с указанием id (object_class + object_id)
    object_class = mapped_column(Enum(TicketAvailableObjectClasses), nullable=False)
    object_id: Mapped[int] = mapped_column(Integer, nullable=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), index=True)
    moderator_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("moderator.id"), nullable=True
    )

    ticket_type = mapped_column(Enum(TicketType), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=True)

    status = mapped_column(Enum(TicketStatus), default=TicketStatus.PENDING)
    moderator_comment: Mapped[str] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="tickets", lazy="selectin")
    moderator: Mapped["Moderator"] = relationship(
        back_populates="answered_tickets", lazy="selectin"
    )

    # Отношение "ОДИН-КО-МНОГИМ" к изображениям тикета (ImageTicket)
    images: Mapped[list["ImageTicket"]] = relationship(
        back_populates="ticket",
        foreign_keys="ImageTicket.ticket_id",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

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
