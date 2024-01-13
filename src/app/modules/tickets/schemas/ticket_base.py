from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


from pydantic_partial import create_partial_model

from app.modules.tickets.utils.classes import TicketType, TicketStatus


class TicketBaseSchema(BaseModel):
    ticket_type: Optional[TicketType] = None
    status: TicketStatus = TicketStatus.PENDING


class TicketCreateSchema(TicketBaseSchema):
    pass


class TicketReadSchema(TicketBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    reason: Optional[str] = None
    moderator_comment: Optional[str] = None

    user_id: int

    discriminator: str
    id: int

    created_at: datetime
    updated_at: datetime

    # class Config:
    #     from_attributes = True


class TicketUpdateSchema(TicketBaseSchema):
    reason: Optional[str] = None
    moderator_comment: Optional[str] = None


TicketUpdateSchema = create_partial_model(TicketUpdateSchema, recursive=True)
