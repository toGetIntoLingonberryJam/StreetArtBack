# from datetime import datetime
#
# from pydantic import Field, ConfigDict
from typing import Optional

from pydantic import model_validator, ConfigDict
import json
from pydantic_partial import create_partial_model

from app.modules.artworks.schemas.artwork import (
    ArtworkCreateSchema,
    ArtworkUpdateSchema,
)
from app.modules.tickets.schemas.ticket_base import (
    TicketBaseSchema,
    TicketCreateSchema,
    TicketReadSchema,
    TicketUpdateSchema,
)


class ArtworkTicketBaseSchema(TicketBaseSchema):
    pass


class ArtworkTicketCreateSchema(TicketCreateSchema, ArtworkTicketBaseSchema):
    artwork_data: ArtworkCreateSchema

    @model_validator(mode="before")
    def validate_to_json(
        cls, value
    ):  # noqa Костыль, без которого не работает multipart/form data заспросы
        if isinstance(value, str):
            return cls(**json.loads(value))  # noqa
        return value


class ArtworkTicketReadSchema(TicketReadSchema, ArtworkTicketBaseSchema):
    # model_config = ConfigDict(from_attributes=True)
    artwork_data: dict


class ArtworkTicketUpdateSchema(TicketUpdateSchema, ArtworkTicketBaseSchema):
    artwork_data: ArtworkUpdateSchema


ArtworkTicketUpdateSchema = create_partial_model(
    ArtworkTicketUpdateSchema, recursive=True
)
