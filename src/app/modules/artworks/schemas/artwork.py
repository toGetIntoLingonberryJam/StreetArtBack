from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator, computed_field, HttpUrl
import json

from app.modules.artworks.models.artwork import ArtworkStatus
from app.modules.artworks.schemas.artwork_image import ArtworkImage
from app.modules.artworks.schemas.artwork_location import ArtworkLocationCreate, ArtworkLocation, ArtworkLocationEdit
from app.modules.artworks.schemas.artwork_moderation import ArtworkModerationBase, ArtworkModerationEdit

from pydantic_partial import create_partial_model


class ArtworkBase(BaseModel):
    title: str
    year_created: int = Field(...,
                              gt=1900, le=datetime.today().year,
                              description='The year of creation cannot be less than 1900 and more than the current '
                                          'year.')
    festival: Optional[str]
    description: str
    source_description: str
    artist_id: int
    status: ArtworkStatus


class ArtworkCreate(ArtworkBase):
    location: Optional[ArtworkLocationCreate]

    @model_validator(mode='before')
    def validate_to_json(cls, value):  # noqa Костыль, без которого не работает multipart/form data заспросы
        if isinstance(value, str):
            return cls(**json.loads(value))  # noqa
        return value


class Artwork(ArtworkBase):
    id: int
    added_by_user_id: int

    location: Optional[ArtworkLocation]
    images: Optional[List[ArtworkImage]]

    created_at: datetime = Field(exclude=True)
    updated_at: datetime

    class Config:
        from_attributes = True


class ArtworkForModerator(Artwork):
    moderation: ArtworkModerationBase


class ArtworkEdit(ArtworkCreate):
    location: Optional[ArtworkLocationEdit]
    added_by_user_id: Optional[int]
    moderation: Optional[ArtworkModerationEdit]


ArtworkEdit = create_partial_model(ArtworkEdit, recursive=True)
