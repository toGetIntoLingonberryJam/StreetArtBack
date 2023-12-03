from typing import List

from fastapi import Depends

from app.modules.users.fastapi_users_config import current_user
from app.modules.users.models import User


def get_favorite_artworks(user: User = Depends(current_user)) -> List[int]:
    return user.favorite_artworks

