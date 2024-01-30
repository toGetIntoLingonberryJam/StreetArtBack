from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.modules.cloud_storage.schemas.image import ImageReadSchema


class ArtistCardSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    image: Optional[ImageReadSchema] = None
