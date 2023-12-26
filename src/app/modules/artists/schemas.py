from typing import Optional, List

from pydantic import BaseModel, AnyUrl

from app.modules.artworks.schemas.artwork import Artwork


class ArtistCreate(BaseModel):
    name: str
    description: str
    # links: List[str]
    user_id: Optional[int] | None = None


class ArtistRead(ArtistCreate):
    id: int
