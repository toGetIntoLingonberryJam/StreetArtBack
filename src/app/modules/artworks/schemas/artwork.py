from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.modules.artworks.models.artwork import ArtworkStatus
from app.modules.artworks.schemas.artwork_image import ArtworkImage
from app.modules.artworks.schemas.artwork_location import ArtworkLocation


class ArtworkBase(BaseModel):
    title: str
    year_created: int = Field(...,
                              gt=1900, le=datetime.today().year,
                              description='The year of creation cannot be less than 1900 and more than the current '
                                          'year.')
    festival: str
    description: str
    source_description: str
    added_by_user_id: int
    artist_id: int
    status: ArtworkStatus


class ArtworkCreate(ArtworkBase):
    location: Optional[ArtworkLocation]
    images: Optional[List[ArtworkImage]]


class Artwork(ArtworkBase):
    id: int
    created_at: datetime
    updated_at: datetime
    location: Optional[ArtworkLocation]
    images: Optional[List[ArtworkImage]]

    class Config:
        from_attributes = True


class ArtworkEdit(BaseModel):
    title: str
    year_created: int = Field(...,
                              gt=1900, le=datetime.today().year,
                              description='The year of creation cannot be less than 1900 and more than the current '
                                          'year.')
    festival: str
    description: str
    source_description: str
    status: ArtworkStatus
