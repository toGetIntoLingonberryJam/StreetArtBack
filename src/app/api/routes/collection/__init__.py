from fastapi import APIRouter

from .likes import collection_router

router = APIRouter(prefix="/collection", tags=["Likes"])

router.include_router(collection_router)
