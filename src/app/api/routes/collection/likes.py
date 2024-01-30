from typing import List

from fastapi import APIRouter, Depends

from app.modules.artists.schemas.artist_card import ArtistCardSchema
from app.modules.artworks.schemas.artwork_card import ArtworkCardSchema
from app.modules.festivals.card_schema import FestivalCardSchema
from app.modules.users.fastapi_users_config import current_user
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
