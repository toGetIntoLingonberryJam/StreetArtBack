from pydantic import AliasChoices, Field

from app.modules.collections.models import LikeType


class LikeSchema:
    id: int
    user_id: int
    object_id: int = Field(
        ..., validation_alias=AliasChoices("artwork_id", "festival_id", "artist_id")
    )
    object_type: LikeType
