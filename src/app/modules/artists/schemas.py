from typing import Optional, List

from pydantic import field_validator, HttpUrl

from app.modules.artists.base_schema import ArtistBase
from app.modules.artworks.schemas.artwork import ArtworkCard


class ArtistCreate(ArtistBase):
    user_id: Optional[int] | None = None

    @field_validator('links')
    def links_validator(cls, v: List[HttpUrl]) -> List[str]:
        return [i.__str__() for i in v]


class ArtistRead(ArtistBase):
    id: int
    artworks: List[ArtworkCard]

    @field_validator('links', mode='before')
    def links_validator(cls, v: List[str]) -> List[str]:
        links = ''.join(v).strip('{}').split(',')
        return links

