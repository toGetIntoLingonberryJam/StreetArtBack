from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.modules import TicketType, TicketStatus

from pydantic_partial import create_partial_model

from app.modules.tickets.schemas.ticket_base import TicketBaseSchema


class ArtworkTicketBaseSchema(TicketBaseSchema):
    user_id: int
    ticket_type: Optional[TicketType] = None
    reason: Optional[str] = None
    status: TicketStatus = TicketStatus.PENDING
    moderator_comment: Optional[str] = None


class ArtworkTicketCreateSchema(ArtworkTicketBaseSchema):
    pass


# class ArtworkTicketUpdate(TicketBase):
#     pass


class ArtworkTicketSchema(ArtworkTicketBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int

    created_at: datetime = Field(exclude=True)
    updated_at: datetime

    # class Config:
    #     from_attributes = True


ArtworkTicketUpdateSchema = create_partial_model(ArtworkTicketBaseSchema, recursive=True)
