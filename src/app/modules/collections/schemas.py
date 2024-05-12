from pydantic import BaseModel
from app.modules.collections.models import LikeType


class LikeSchema(BaseModel):
    id: int
    is_liked: bool = False
    object_type: LikeType
