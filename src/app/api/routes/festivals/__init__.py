from fastapi import APIRouter

from .festivals import festival_router

router = APIRouter(prefix="/festivals", tags=["Festivals"])

router.include_router(festival_router)
