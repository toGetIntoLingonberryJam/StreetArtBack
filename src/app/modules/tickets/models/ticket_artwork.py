from sqlalchemy import JSON, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.tickets.models.ticket_base import TicketBase
from app.modules.tickets.utils.classes import TicketModel, TicketRegistry


@TicketRegistry.register(TicketModel.TICKET_ARTWORK)
class TicketArtwork(TicketBase):
    __tablename__ = TicketModel.TICKET_ARTWORK.value

    id: Mapped[int] = mapped_column(None, ForeignKey("ticket.id"), primary_key=True)

    # Просто JSON, т.к. за время разработки/поддержки приложения схема может измениться
    artwork_data: Mapped[dict] = mapped_column(JSON, nullable=True)

    __mapper_args__ = {"polymorphic_identity": TicketModel.TICKET_ARTWORK.value}

    # def __init__(self, ticket_type, user_id, reason, artwork_id=None, artwork_data=None):
    #     super().__init__(ticket_type=ticket_type, user_id=user_id, reason=reason)
    #     self.artwork_id = artwork_id
    #     self.artwork_data = artwork_data
