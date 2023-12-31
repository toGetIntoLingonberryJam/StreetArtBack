from sqlalchemy import JSON, Integer, ForeignKey
from sqlalchemy.orm import mapped_column

from app.modules.tickets.models.base_ticket import TicketBase


class ArtworkTicket(TicketBase):
    artwork_id = mapped_column(Integer, ForeignKey("artwork.id"), index=True, nullable=True)
    artwork_data = mapped_column(JSON, nullable=True)

    __mapper_args__ = {"polymorphic_identity": "artwork_ticket"}

    # def __init__(self, ticket_type, user_id, reason, artwork_id=None, artwork_data=None):
    #     super().__init__(ticket_type=ticket_type, user_id=user_id, reason=reason)
    #     self.artwork_id = artwork_id
    #     self.artwork_data = artwork_data
