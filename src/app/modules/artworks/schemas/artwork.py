from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator, ConfigDict, field_validator
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
    description: str
    source_description: str
    artist_id: Optional[int]
    festival_id: Optional[int]
    status: ArtworkStatus


class ArtworkCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    artist_id: Optional[int]
    festival_id: Optional[int]
    status: ArtworkStatus
    images: Optional[List[ArtworkImage]] = Field(..., exclude=True)
    location: ArtworkLocation = Field(..., exclude=True)

    address: Optional[str] = None
    card_image: Optional[ArtworkImage] = None

    @field_validator("images")
    def images_valid(cls, img: List[ArtworkImage] | None) -> Optional[List[ArtworkImage]]:
        if img:
            cls.card_image = img[0]
        return img

    @field_validator("location")
    def loc_valid(cls, location: ArtworkLocation) -> ArtworkLocation:
        cls.address = location.address
        return location


class ArtworkCreate(ArtworkBase):
    location: ArtworkLocationCreate

    @model_validator(mode='before')
    def validate_to_json(cls, value):  # noqa Костыль, без которого не работает multipart/form data заспросы
        if isinstance(value, str):
            return cls(**json.loads(value))  # noqa
        return value


class Artwork(ArtworkBase):
    id: int
    added_by_user_id: int

    location: ArtworkLocation
    images: Optional[List[ArtworkImage]]

    created_at: datetime = Field(exclude=True)
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArtworkForModerator(Artwork):
    moderation: ArtworkModerationBase


class ArtworkEdit(ArtworkCreate):
    location: Optional[ArtworkLocationEdit]
    added_by_user_id: Optional[int]
    moderation: Optional[ArtworkModerationEdit]
    artist_id: Optional[int]


ArtworkEdit = create_partial_model(ArtworkEdit, recursive=True)
