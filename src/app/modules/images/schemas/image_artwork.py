from pydantic_partial import create_partial_model

from app.modules.images.schemas.image import (
    ImageBaseSchema,
    ImageCreateSchema,
    ImageReadSchema,
)


class ImageArtworkBaseSchema(ImageBaseSchema):
    artwork_id: int


class ImageArtworkCreateSchema(ImageCreateSchema, ImageArtworkBaseSchema):
    pass


class ImageArtworkReadSchema(ImageReadSchema, ImageArtworkBaseSchema):
    pass


class ImageArtworkUpdateSchema(ImageArtworkBaseSchema):
    pass


ImageArtworkUpdateSchema = create_partial_model(ImageArtworkUpdateSchema, recursive=True)
