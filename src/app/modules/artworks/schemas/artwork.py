import json
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator
from pydantic_partial import create_partial_model

from app.modules.artists.schemas.artist_card import ArtistCardSchema
from app.modules.artworks.models.artwork import ArtworkStatus
from app.modules.artworks.schemas.artwork_location import (
    ArtworkLocationBaseSchema,
    ArtworkLocationReadSchema,
    ArtworkLocationUpdateSchema,
)
from app.modules.artworks.schemas.artwork_moderation import (
    ArtworkModerationBaseSchema,
    ArtworkModerationUpdateSchema,
)
from app.modules.festivals.card_schema import FestivalCardSchema
from app.modules.images.schemas.image_artwork import ImageArtworkReadSchema


class ArtworkBaseSchema(BaseModel):
    title: str
    year_created: Optional[int] = Field(
        None,
        ge=1900,
        le=datetime.today().year,
        description="The year of creation cannot be less than 1900 and more than the current "
        "year.",
    )
    description: Optional[str] = None
    artist_id: Optional[int]
    festival_id: Optional[int]
    status: ArtworkStatus

    links: Optional[List[HttpUrl]] = Field(None, description="List of URLs related to the artwork")

    # model_config = ConfigDict(validate_assignment=True)  # Отключаем кеширование

    @model_validator(mode="before")
    def urls_to_strings(cls, values):
        if not isinstance(values, cls):
            return values

        if "links" in values and values["links"] is not None:
            values["links"] = [str(url) for url in values["links"]]
        return values

    # @model_validator(mode="after")
    # def strings_to_urls(cls, values):
    #     if "links" in values and values["links"] is not None:
    #         values["links"] = [HttpUrl(url) for url in values["links"]]
    #     return values


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
    images: Optional[List[ImageArtworkReadSchema]]
    artist: Optional[ArtistCardSchema]
    festival: Optional[FestivalCardSchema]

    created_at: Optional[datetime] = Field(None, exclude=True)
    updated_at: datetime


class ArtworkForModeratorReadSchema(ArtworkReadSchema):
    moderation: ArtworkModerationBaseSchema


class ArtworkUpdateSchema(ArtworkCreateSchema):
    location: Optional[ArtworkLocationUpdateSchema]
    added_by_user_id: Optional[int]
    moderation: Optional[ArtworkModerationUpdateSchema]


ArtworkUpdateSchema = create_partial_model(ArtworkUpdateSchema, recursive=True)
