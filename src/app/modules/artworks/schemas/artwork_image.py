from pydantic import BaseModel, HttpUrl


class ArtworkImageBase(BaseModel):
    image_url: HttpUrl
    # thumbnail_url: Optional[HttpUrl]


class ArtworkImageCreate(ArtworkImageBase):
    artwork_id: int


class ArtworkImage(ArtworkImageBase):
    id: int
    # artwork_id: int


class ArtworkImageThumbnail(BaseModel):
    thumbnail_url: HttpUrl
