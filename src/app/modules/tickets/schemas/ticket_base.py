import json
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_partial import create_partial_model

from app.modules.images.schemas.image import ImageReadSchema
from app.modules.tickets.utils.classes import (
    TicketAvailableObjectClasses,
    TicketStatus,
    TicketType,
)


class TicketBaseSchema(BaseModel):
    reason: Optional[str] = None


class TicketCreateSchema(TicketBaseSchema):
    @model_validator(mode="before")
    def validate_to_json(
        cls, value
    ):  # noqa Костыль, без которого не работает multipart/form data заспросы
        if isinstance(value, str):
            return cls(**json.loads(value))  # noqa
        return value


class TicketReadSchema(TicketBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    object_class: TicketAvailableObjectClasses
    object_id: int | None

    ticket_type: TicketType
    status: TicketStatus = TicketStatus.PENDING
    moderator_comment: Optional[str] = None

    user_id: int
    moderator_id: Optional[int] = None

    discriminator: str
    id: int

    images: Optional[List[ImageReadSchema]]

    created_at: datetime
    updated_at: datetime

    # class Config:
    #     from_attributes = True


class TicketUpdateSchema(TicketBaseSchema):
    reason: Optional[str] = None
    moderator_comment: Optional[str] = None


TicketUpdateSchema = create_partial_model(TicketUpdateSchema, recursive=True)
