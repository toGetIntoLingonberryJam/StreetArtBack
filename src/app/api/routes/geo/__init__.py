from fastapi import APIRouter

from .geo import router as geo_router

router = APIRouter(prefix="/geo")

router.include_router(geo_router)
