from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator
import json

from app.modules.artworks.models.artwork import ArtworkStatus
from app.modules.artworks.schemas.artwork_image import ArtworkImage, ArtworkImageCreate
from app.modules.artworks.schemas.artwork_location import ArtworkLocationCreate, ArtworkLocationBase, ArtworkLocation


class ArtworkBase(BaseModel):
    title: str
    year_created: int = Field(...,
                              gt=1900, le=datetime.today().year,
                              description='The year of creation cannot be less than 1900 and more than the current '
                                          'year.')
    festival: Optional[str]
    description: str
    source_description: str
    added_by_user_id: int
    artist_id: int
    status: ArtworkStatus


class ArtworkCreate(ArtworkBase):
    location: Optional[ArtworkLocationCreate]
    # images: Optional[List[ArtworkImageCreate]]

    @model_validator(mode='before')
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class Artwork(ArtworkBase):
    id: int
    created_at: datetime
    updated_at: datetime
    location: Optional[ArtworkLocation]
    images: Optional[List[ArtworkImage]]

    class Config:
        from_attributes = True


class ArtworkEdit(BaseModel):
    title: str
    year_created: int = Field(...,
                              gt=1900, le=datetime.today().year,
                              description='The year of creation cannot be less than 1900 and more than the current '
                                          'year.')
    festival: str
    description: str
    source_description: str
    status: ArtworkStatus
