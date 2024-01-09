from fastapi import APIRouter

from . import artists

router = APIRouter()

router.include_router(artists.artist_router)
