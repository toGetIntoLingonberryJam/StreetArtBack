from typing import Optional, List

from pydantic import BaseModel, AnyUrl

from app.modules.artworks.schemas.artwork import Artwork


class ArtistCreate(BaseModel):
    name: str
    user_id: Optional[int]


class ArtistRead(BaseModel):
    name: str
    description: str
    links: List[AnyUrl]
    artworks: Optional[List[Artwork]]

