from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator, ConfigDict
import json

from app.modules.artworks.models.artwork import ArtworkStatus
from app.modules.artworks.schemas.artwork_image import ArtworkImageReadSchema
from app.modules.artworks.schemas.artwork_location import (
    ArtworkLocationReadSchema,
    ArtworkLocationUpdateSchema,
    ArtworkLocationBaseSchema,
)
from app.modules.artworks.schemas.artwork_moderation import (
    ArtworkModerationBaseSchema,
    ArtworkModerationUpdateSchema,
)

from pydantic_partial import create_partial_model


class ArtworkBaseSchema(BaseModel):
    title: str
    year_created: int = Field(
        ...,
        gt=1900,
        le=datetime.today().year,
        description="The year of creation cannot be less than 1900 and more than the current "
        "year.",
    )
    festival: Optional[str]
    description: str
    source_description: str
    artist_id: int
    status: ArtworkStatus


class ArtworkCreateSchema(ArtworkBaseSchema):
    location: ArtworkLocationBaseSchema

    @model_validator(mode="before")
    def validate_to_json(
        cls, value
    ):  # noqa Костыль, без которого не работает multipart/form data заспросы
        if isinstance(value, str):
            return cls(**json.loads(value))  # noqa
        return value


class ArtworkReadSchema(ArtworkBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    added_by_user_id: int

    location: ArtworkLocationReadSchema
    images: Optional[List[ArtworkImageReadSchema]]

    created_at: datetime = Field(exclude=True)
    updated_at: datetime

    # class Config:
    #     from_attributes = True


class ArtworkForModeratorReadSchema(ArtworkReadSchema):
    moderation: ArtworkModerationBaseSchema


class ArtworkUpdateSchema(ArtworkCreateSchema):
    location: Optional[ArtworkLocationUpdateSchema]
    added_by_user_id: Optional[int]
    moderation: Optional[ArtworkModerationUpdateSchema]


ArtworkUpdateSchema = create_partial_model(ArtworkUpdateSchema, recursive=True)
