from typing import Optional

from pydantic import BaseModel
from pydantic_partial import PartialModelMixin

from app.modules.artworks.models.artwork_moderation import ArtworkModerationStatus


class ArtworkModerationBase(BaseModel):
    comment: Optional[str] = None
    status: ArtworkModerationStatus = ArtworkModerationStatus.PENDING


class ArtworkModerationCreate(ArtworkModerationBase):
    artwork_id: int


class ArtworkModerationEdit(PartialModelMixin, ArtworkModerationBase):
    pass


class ArtworkModeration(ArtworkModerationBase):
    artwork_id: int
