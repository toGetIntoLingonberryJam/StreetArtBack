from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, computed_field

from app.modules.artists.schemas.artist_card import ArtistCardSchema
from app.modules.artworks.models.artwork import ArtworkStatus
from app.modules.artworks.schemas.artwork_location import ArtworkLocationReadSchema
from app.modules.festivals.card_schema import FestivalCardSchema
from app.modules.images.schemas.image_artwork import ImageArtworkReadSchema


class ArtworkCardSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    festival: Optional[FestivalCardSchema]
    status: ArtworkStatus
    images: Optional[List[ImageArtworkReadSchema]] = Field(..., exclude=True)
    location: ArtworkLocationReadSchema = Field(..., exclude=True)
    artist: Optional[ArtistCardSchema]

    @computed_field
    @property
    def image(self) -> Optional[ImageArtworkReadSchema]:
        if self.images and len(self.images) > 0:
            return self.images[0]

    # @computed_field
    # @property
    # def preview_image(self) -> Optional[HttpUrl]:
    #     if self.images and len(self.images) > 0:
    #         return self.images[0].image_url

    @computed_field
    @property
    def address(self) -> str:
        return self.location.address
