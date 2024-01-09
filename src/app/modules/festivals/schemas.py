from typing import List

from pydantic import BaseModel, HttpUrl, field_validator, ConfigDict

from app.modules.artworks.schemas.artwork_card import ArtworkCardSchema


class FestivalBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str
    links: List[HttpUrl]


class FestivalCreateSchema(FestivalBaseSchema):
    @field_validator("links")
    def links_validator(cls, v: List[HttpUrl]) -> List[str]:
        return [i.__str__() for i in v]


class FestivalReadSchema(FestivalBaseSchema):
    id: int
    artworks: List[ArtworkCardSchema]

    @field_validator("links", mode="before")
    def links_validator(cls, v: List[str]) -> List[str]:
        links = "".join(v).strip("{}").split(",")
        return links
