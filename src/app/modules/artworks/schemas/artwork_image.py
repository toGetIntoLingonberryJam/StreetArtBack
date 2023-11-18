from pydantic import BaseModel, HttpUrl


class ArtworkImageBase(BaseModel):
    image_url: HttpUrl


class ArtworkImageCreate(ArtworkImageBase):
    image_url: str
    artwork_id: int


class ArtworkImage(ArtworkImageBase):
    id: int


# class ArtworkImageThumbnail(BaseModel):
#     thumbnail_url: HttpUrl
