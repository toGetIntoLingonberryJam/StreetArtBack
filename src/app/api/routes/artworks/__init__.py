from fastapi import APIRouter

from .artworks import router_artworks

router = APIRouter(prefix="/artworks")

router.include_router(router_artworks)
