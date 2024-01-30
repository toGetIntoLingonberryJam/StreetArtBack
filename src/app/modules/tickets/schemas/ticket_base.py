from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


from pydantic_partial import create_partial_model

from app.modules.tickets.utils.classes import TicketType, TicketStatus


class TicketBaseSchema(BaseModel):
    ticket_type: Optional[TicketType] = None
    reason: Optional[str] = None
    status: TicketStatus = TicketStatus.PENDING
    moderator_comment: Optional[str] = None


class TicketCreateSchema(TicketBaseSchema):
    pass


class TicketReadSchema(TicketBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    user_id: int

    discriminator: str
    id: int

    created_at: datetime
    updated_at: datetime

    # class Config:
    #     from_attributes = True


class TicketUpdateSchema(TicketBaseSchema):
    pass


TicketUpdateSchema = create_partial_model(TicketUpdateSchema, recursive=True)
