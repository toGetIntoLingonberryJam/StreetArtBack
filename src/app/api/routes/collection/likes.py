from typing import List, Union

from fastapi import APIRouter, Depends, Query, HTTPException
from starlette import status

from app.modules.artists.schemas.artist_card import ArtistCardSchema
from app.modules.artworks.schemas.artwork_card import ArtworkCardSchema
from app.modules.collections.models import LikeType
from app.modules.collections.schemas import LikeSchema
from app.modules.festivals.card_schema import FestivalCardSchema
from app.modules.users.fastapi_users_config import current_user, current_nullable_user
from app.modules.users.models import User
from app.services.user import UserService
from app.utils.dependencies import UOWDep

collection_router = APIRouter()


@collection_router.get("/artworks", response_model=List[ArtworkCardSchema])
async def get_favorite_artworks(uow: UOWDep, user: User = Depends(current_user)):
    likes = await UserService().get_artwork_likes(uow, user.id)
    return likes


@collection_router.get("/artists", response_model=List[ArtistCardSchema])
async def get_favorite_artists(uow: UOWDep, user: User = Depends(current_user)):
    likes = await UserService().get_artist_likes(uow, user.id)
    return likes


@collection_router.get("/festivals", response_model=List[FestivalCardSchema])
async def get_favorite_festivals(uow: UOWDep, user: User = Depends(current_user)):
    likes = await UserService().get_festival_likes(uow, user.id)
    return likes


@collection_router.get("/like_status", response_model=List[LikeSchema])
async def get_object_like_status(
    object_type: LikeType,
    uow: UOWDep,
    object_ids: str = Query(None, description="ID объектов, разделенные запятыми"),
    user: User = Depends(current_nullable_user),
):
    try:
        ids = list(map(int, object_ids.split(",")))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid object IDs"
        )
    result = []
    for obj_id in ids:
        if obj_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid object IDs"
            )
        is_liked = await UserService().get_user_status_like(
            uow, user.id if user else None, object_type, obj_id
        )
        result.append({"id": obj_id, "is_liked": is_liked, "object_type": object_type})
    return result
