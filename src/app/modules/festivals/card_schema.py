from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.modules.images.schemas.image import ImageReadSchema


class FestivalCardSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    image: Optional[ImageReadSchema] = None
