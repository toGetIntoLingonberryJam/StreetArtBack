from typing import Optional

from pydantic import BaseModel, field_validator, HttpUrl
from pydantic_partial import PartialModelMixin

from app.modules.artworks.models.artwork_image import ArtworkImage


class ArtworkLocationBaseSchema(BaseModel):
    latitude: float
    longitude: float
    address: str


class ArtworkLocationCreateSchema(ArtworkLocationBaseSchema):
    artwork_id: int


class ArtworkLocationUpdateSchema(PartialModelMixin, ArtworkLocationBaseSchema):
    pass


class ArtworkLocationReadSchema(ArtworkLocationBaseSchema):
    artwork_id: int

    thumbnail_image: Optional[HttpUrl]

    @field_validator("thumbnail_image", mode="before")
    def validate_image(cls, v):  # noqa
        if v:
            # Если значение - строка, вернуть его как URL-адрес
            if isinstance(v, ArtworkImage):
                return v.image_url
            return v
