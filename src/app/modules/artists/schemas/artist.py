import json
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator, model_validator

from app.modules.artworks.schemas.artwork_card import ArtworkCardSchema
from app.modules.images.schemas.image import ImageReadSchema


class ArtistBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: Optional[str]
    links: Optional[List[HttpUrl]] = None


class ArtistCreateSchema(ArtistBaseSchema):
    user_id: Optional[int] = None

    @field_validator("links")
    def links_validator(cls, v: List[HttpUrl]) -> List[str]:
        if v:
            return [i.__str__() for i in v]

    @model_validator(mode="before")
    def validate_to_json(
        cls, value
    ):  # noqa Костыль, без которого не работает multipart/form data заспросы
        if isinstance(value, str):
            return cls(**json.loads(value))  # noqa
        return value


class ArtistReadSchema(ArtistBaseSchema):
    id: int
    image: Optional[ImageReadSchema] = None
    # artworks: Optional[List[ArtworkCardSchema]] = None

    # @field_validator("links", mode="before")
    # def links_validator(cls, v: List[str]) -> List[str]:
    #     links = "".join(v).strip("{}").split(",")
    #     return links
