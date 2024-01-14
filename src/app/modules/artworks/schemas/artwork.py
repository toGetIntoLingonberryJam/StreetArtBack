from datetime import datetime
from typing import List, Optional

from pydantic import (
    BaseModel,
    Field,
    model_validator,
    ConfigDict,
    field_validator,
    HttpUrl,
)
import json

from app.modules.artists.schemas.artist_card import ArtistCardSchema
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
    description: Optional[str] = None
    source_description: Optional[str] = None
    artist_id: Optional[int]
    festival_id: Optional[int]
    status: ArtworkStatus
    links: Optional[List[HttpUrl]] = None


class ArtworkCreateSchema(ArtworkBaseSchema):
    location: ArtworkLocationBaseSchema

    @model_validator(mode="before")
    def validate_to_json(
            cls, value
    ):  # noqa Костыль, без которого не работает multipart/form data заспросы
        if isinstance(value, str):
            return cls(**json.loads(value))  # noqa
        return value

    @field_validator("links")
    def links_validator(cls, v: List[HttpUrl]) -> List[str]:
        if v:
            return [i.__str__() for i in v]


class ArtworkReadSchema(ArtworkBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    added_by_user_id: int

    location: ArtworkLocationReadSchema
    images: Optional[List[ArtworkImageReadSchema]]
    artist: Optional[ArtistCardSchema]

    created_at: datetime = Field(exclude=True)
    updated_at: datetime

    @field_validator("links", mode="before")
    def links_validator(cls, v: List[str]) -> List[str]:
        if v:
            links = "".join(v).strip("{}").split(",")
            return links


class ArtworkForModeratorReadSchema(ArtworkReadSchema):
    moderation: ArtworkModerationBaseSchema


class ArtworkUpdateSchema(ArtworkCreateSchema):
    location: Optional[ArtworkLocationUpdateSchema]
    added_by_user_id: Optional[int]
    moderation: Optional[ArtworkModerationUpdateSchema]


ArtworkUpdateSchema = create_partial_model(ArtworkUpdateSchema, recursive=True)
