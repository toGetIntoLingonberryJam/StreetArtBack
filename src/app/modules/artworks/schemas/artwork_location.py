from typing import Optional

from pydantic import BaseModel, field_validator, HttpUrl


class ArtworkLocationBase(BaseModel):
    latitude: float
    longitude: float
    address: str
    artwork_id: int


class ArtworkLocationCreate(ArtworkLocationBase):
    pass


class ArtworkLocation(ArtworkLocationBase):
    thumbnail_image: Optional[HttpUrl]

    @field_validator('thumbnail_image', mode='before')
    def validate_image(cls, v):
        return v.thumbnail_url




