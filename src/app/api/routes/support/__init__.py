from fastapi import APIRouter

from .tickets import router as tickets_router

router = APIRouter(prefix="/support", tags=["Support"])

router.include_router(tickets_router)
