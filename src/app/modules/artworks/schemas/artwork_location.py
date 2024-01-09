from typing import Optional

from pydantic import BaseModel, field_validator, HttpUrl, ConfigDict, Field
from pydantic_partial import PartialModelMixin

from app.modules.artworks.models.artwork_image import ArtworkImage


class ArtworkLocationBase(BaseModel):
    latitude: float
    longitude: float
    address: str


class ArtworkLocationCreate(ArtworkLocationBase):
    pass


class ArtworkLocationEdit(PartialModelMixin, ArtworkLocationCreate):
    pass


class ArtworkLocation(ArtworkLocationBase):
    artwork_id: int

    thumbnail_image: Optional[HttpUrl]

    @field_validator("thumbnail_image", mode="before")
    def validate_image(cls, v):  # noqa
        if v:
            # Если значение - строка, вернуть его как URL-адрес
            if isinstance(v, ArtworkImage):
                return v.image_url
            return v
