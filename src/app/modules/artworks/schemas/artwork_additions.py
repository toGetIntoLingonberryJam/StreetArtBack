from pydantic import BaseModel


class ArtworkAdditionsBase(BaseModel):
    pass


class ArtworkAdditionsCreate(ArtworkAdditionsBase):
    artwork_id: int


class ArtworkAdditions(ArtworkAdditionsBase):
    id: int
    artwork_id: int
    # images: List[ArtworkImage]
