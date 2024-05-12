from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, computed_field

from app.modules.cloud_storage.schemas.image import ImageReadSchema


class ArtistCardSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    image: Optional[ImageReadSchema] = Field(exclude=True)

    @computed_field
    @property
    def preview_image(self) -> Optional[HttpUrl]:
        if self.image:
            return self.image.image_url
