from typing import Optional

from pydantic import BaseModel, HttpUrl, field_validator
from pydantic_partial import PartialModelMixin

from app.modules.images.models import ImageArtwork


class ArtworkLocationBaseSchema(BaseModel):
    latitude: float
    longitude: float
    address: str


class ArtworkLocationCreateSchema(ArtworkLocationBaseSchema):
    artwork_id: int


class ArtworkLocationTicketCreateSchema(ArtworkLocationCreateSchema):
    thumbnail_image_id: Optional[int]


class ArtworkLocationUpdateSchema(PartialModelMixin, ArtworkLocationBaseSchema):
    pass


class ArtworkLocationReadSchema(ArtworkLocationBaseSchema):
    artwork_id: int

    thumbnail_image: Optional[HttpUrl]

    @field_validator("thumbnail_image", mode="before")
    def validate_image(cls, v):  # noqa
        if v:
            # Если значение - строка, вернуть его как URL-адрес
            if isinstance(v, ImageArtwork):
                return v.image_url
            if isinstance(v, dict):  # Костыль для кэширования
                return v.get("image_url")
            return v
