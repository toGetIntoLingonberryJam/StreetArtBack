from pydantic_partial import create_partial_model

from app.modules.cloud_storage.schemas.image import (
    ImageBaseSchema,
    ImageCreateSchema,
    ImageReadSchema,
)


class ArtworkImageBaseSchema(ImageBaseSchema):
    artwork_id: int


class ArtworkImageCreateSchema(ImageCreateSchema, ArtworkImageBaseSchema):
    pass


class ArtworkImageReadSchema(ImageReadSchema, ArtworkImageBaseSchema):
    pass


class ArtworkImageUpdateSchema(ArtworkImageBaseSchema):
    pass


ArtworkImageUpdateSchema = create_partial_model(
    ArtworkImageUpdateSchema, recursive=True
)
