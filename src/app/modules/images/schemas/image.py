from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl, constr
from pydantic_partial import create_partial_model


class ImageBaseSchema(BaseModel):
    image_url: str
    blurhash: Optional[str] = None
    description: Optional[constr(max_length=50)] = None


class ImageCreateSchema(ImageBaseSchema):
    public_key: str
    file_path: str


class ImageReadSchema(ImageBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    # discriminator: str
    id: int


class ImageUpdateSchema(ImageBaseSchema):
    pass


ImageUpdateSchema = create_partial_model(ImageUpdateSchema, recursive=True)
