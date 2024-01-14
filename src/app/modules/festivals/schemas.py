from typing import List, Optional
import json

from pydantic import BaseModel, HttpUrl, field_validator, ConfigDict, model_validator

from app.modules.artworks.schemas.artwork_card import ArtworkCardSchema
from app.modules.cloud_storage.schemas.image import ImageReadSchema


class FestivalBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str
    links: Optional[List[HttpUrl]] = None


class FestivalCreateSchema(FestivalBaseSchema):
    @field_validator("links")
    def links_validator(cls, v: List[HttpUrl]) -> List[str]:
        return [i.__str__() for i in v]

    @model_validator(mode="before")
    def validate_to_json(
            cls, value
    ):  # noqa Костыль, без которого не работает multipart/form data заспросы
        if isinstance(value, str):
            return cls(**json.loads(value))  # noqa
        return value


class FestivalReadSchema(FestivalBaseSchema):
    id: int
    artworks: List[ArtworkCardSchema]
    image: Optional[ImageReadSchema] = None

    # @field_validator("links", mode="before")
    # def links_validator(cls, v: List[str]) -> List[str]:
    #     links = "".join(v).strip("{}").split(",")
    #     return links
