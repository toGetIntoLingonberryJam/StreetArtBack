from pydantic import BaseModel, HttpUrl


class ArtworkImageBaseSchema(BaseModel):
    image_url: HttpUrl


class ArtworkImageCreateSchema(ArtworkImageBaseSchema):
    image_url: str
    artwork_id: int


class ArtworkImageReadSchema(ArtworkImageBaseSchema):
    id: int
