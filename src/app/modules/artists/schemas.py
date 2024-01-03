from typing import Optional, List

from pydantic import BaseModel, ConfigDict, field_validator, HttpUrl


class ArtistCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str
    links: List[HttpUrl]
    user_id: Optional[int] | None = None

    @field_validator('links')
    def links_validator(cls, v: List[HttpUrl]) -> List[str]:
        return [i.__str__() for i in v]


class ArtistRead(ArtistCreate):
    id: int

    @field_validator('links', mode='before')
    def links_validator(cls, v: List[str]) -> List[str]:
        links = ''.join(v).strip('{}').split(',')
        return links
