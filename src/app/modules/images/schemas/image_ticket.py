from pydantic_partial import create_partial_model

from app.modules.images.schemas.image import (
    ImageBaseSchema,
    ImageCreateSchema,
    ImageReadSchema,
)


class ImageTicketBaseSchema(ImageBaseSchema):
    pass


class ImageTicketCreateSchema(ImageCreateSchema, ImageTicketBaseSchema):
    ticket_id: int


class ImageTicketReadSchema(ImageReadSchema, ImageTicketBaseSchema):
    pass


class ImageTicketUpdateSchema(ImageTicketBaseSchema):
    pass


ImageTicketUpdateSchema = create_partial_model(ImageTicketUpdateSchema, recursive=True)
