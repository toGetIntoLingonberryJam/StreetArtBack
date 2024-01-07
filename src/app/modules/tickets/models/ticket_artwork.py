from sqlalchemy import JSON, Integer, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from app.modules.tickets.models.ticket_base import TicketBase
from app.modules.tickets.utils.classes import TicketModel, TicketRegistry


@TicketRegistry.register(TicketModel.ARTWORK_TICKET)
class ArtworkTicket(TicketBase):
    __tablename__ = "artwork_ticket"
    id: Mapped[int] = mapped_column(None, ForeignKey("ticket.id"), primary_key=True)

    artwork_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("artwork.id"), index=True, nullable=True
    )
    artwork_data: Mapped[dict] = mapped_column(JSON, nullable=True)

    __mapper_args__ = {"polymorphic_identity": TicketModel.ARTWORK_TICKET}

    # def __init__(self, ticket_type, user_id, reason, artwork_id=None, artwork_data=None):
    #     super().__init__(ticket_type=ticket_type, user_id=user_id, reason=reason)
    #     self.artwork_id = artwork_id
    #     self.artwork_data = artwork_data
