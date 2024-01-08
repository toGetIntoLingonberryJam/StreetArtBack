from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.artists.schemas.artist_card import ArtistCard
from app.modules.artworks.models.artwork import ArtworkStatus
from app.modules.artworks.schemas.artwork_image import ArtworkImage
from app.modules.artworks.schemas.artwork_location import ArtworkLocation


class ArtworkCard(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str

    festival_id: Optional[int]
    status: ArtworkStatus
    images: Optional[List[ArtworkImage]] = Field(..., exclude=True)
    location: ArtworkLocation = Field(..., exclude=True)
    artist: Optional[ArtistCard]

    address: Optional[str] = None
    card_image: Optional[ArtworkImage] = None

    @field_validator("images")
    def images_valid(cls, img: List[ArtworkImage] | None) -> Optional[List[ArtworkImage]]:
        if img:
            cls.card_image = img[0]
        return img

    @field_validator("location")
    def loc_valid(cls, location: ArtworkLocation) -> ArtworkLocation:
        cls.address = location.address
        return location