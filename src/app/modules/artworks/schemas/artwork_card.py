from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.artists.schemas.artist_card import ArtistCardSchema
from app.modules.artworks.models.artwork import ArtworkStatus
from app.modules.artworks.schemas.artwork_image import ArtworkImageReadSchema
from app.modules.artworks.schemas.artwork_location import ArtworkLocationReadSchema
from app.modules.festivals.card_schema import FestivalCardSchema
from app.modules.users.schemas import UserRead


class ArtworkCardSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str

    festival: Optional[FestivalCardSchema]
    status: ArtworkStatus
    images: Optional[List[ArtworkImageReadSchema]] = Field(..., exclude=True)
    location: ArtworkLocationReadSchema = Field(..., exclude=True)
    artist: Optional[ArtistCardSchema]

    address: Optional[str] = None
    # is_liked: bool = Field(default=False)
    # likes: Optional[List[UserRead]] = Field(..., exclude=True)
    card_image: Optional[ArtworkImageReadSchema] = None

    @field_validator("images")
    def images_valid(
        cls, img: List[ArtworkImageReadSchema] | None
    ) -> Optional[List[ArtworkImageReadSchema]]:
        if img:
            cls.card_image = img[0]
        return img

    @field_validator("location")
    def loc_valid(
        cls, location: ArtworkLocationReadSchema
    ) -> ArtworkLocationReadSchema:
        cls.address = location.address
        return location
