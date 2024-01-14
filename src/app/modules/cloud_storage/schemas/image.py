from datetime import datetime
from pydantic import BaseModel, ConfigDict
from pydantic_partial import create_partial_model


class ImageBaseSchema(BaseModel):
    image_url: str


class ImageCreateSchema(ImageBaseSchema):
    public_key: str
    file_path: str


class ImageReadSchema(ImageBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    # discriminator: str
    # id: int

    created_at: datetime

    # class Config:
    #     from_attributes = True


class ImageUpdateSchema(ImageBaseSchema):
    pass


ImageUpdateSchema = create_partial_model(ImageUpdateSchema, recursive=True)
