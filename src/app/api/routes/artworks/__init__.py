from fastapi import APIRouter

from . import artworks

router = APIRouter(prefix="/artworks")

router.include_router(artworks.router_artworks)
