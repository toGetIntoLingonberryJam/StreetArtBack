from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.modules import TicketType, TicketStatus

from pydantic_partial import create_partial_model


class TicketBaseSchema(BaseModel):
    user_id: int
    ticket_type: Optional[TicketType] = None
    reason: Optional[str] = None
    status: TicketStatus = TicketStatus.PENDING
    moderator_comment: Optional[str] = None


class TicketCreateSchema(TicketBaseSchema):
    pass


# class TicketUpdate(TicketBase):
#     pass


class TicketSchema(TicketBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int

    created_at: datetime = Field(exclude=True)
    updated_at: datetime

    # class Config:
    #     from_attributes = True


TicketUpdateSchema = create_partial_model(TicketBaseSchema, recursive=True)
