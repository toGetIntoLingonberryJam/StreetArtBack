from typing import Optional

from pydantic import BaseModel
from pydantic_partial import PartialModelMixin

from app.modules.artworks.models.artwork_moderation import ArtworkModerationStatus


class ArtworkModerationBaseSchema(BaseModel):
    comment: Optional[str] = None
    status: ArtworkModerationStatus = ArtworkModerationStatus.PENDING


class ArtworkModerationCreateSchema(ArtworkModerationBaseSchema):
    artwork_id: int


class ArtworkModerationUpdateSchema(PartialModelMixin, ArtworkModerationBaseSchema):
    pass


class ArtworkModerationReadSchema(ArtworkModerationBaseSchema):
    artwork_id: int
