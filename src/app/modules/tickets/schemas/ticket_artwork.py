# from datetime import datetime
#
# from pydantic import Field, ConfigDict
import json
from typing import Optional

from pydantic import ConfigDict, Field, model_validator
from pydantic_partial import create_partial_model

from app.modules.artworks.schemas.artwork import ArtworkCreateSchema, ArtworkUpdateSchema
from app.modules.tickets.schemas.ticket_base import (
    TicketBaseSchema,
    TicketCreateSchema,
    TicketReadSchema,
    TicketUpdateSchema,
)


class TicketArtworkBaseSchema(TicketBaseSchema):
    pass
    # images: Optional[List[ImageReadSchema]] = Field(exclude=True)


class TicketArtworkCreateSchema(TicketCreateSchema, TicketArtworkBaseSchema):
    artwork_data: Optional[ArtworkCreateSchema] = None

    @model_validator(mode="before")
    def validate_to_json(
        cls, value
    ):  # noqa Костыль, без которого не работает multipart/form data заспросы
        if isinstance(value, str):
            return cls(**json.loads(value))  # noqa
        return value


class TicketArtworkReadSchema(TicketReadSchema, TicketArtworkBaseSchema):
    # model_config = ConfigDict(from_attributes=True)
    artwork_data: dict


class TicketArtworkUpdateSchema(TicketUpdateSchema, TicketArtworkBaseSchema):
    artwork_data: ArtworkUpdateSchema


TicketArtworkUpdateSchema = create_partial_model(
    TicketArtworkUpdateSchema, recursive=True
)
