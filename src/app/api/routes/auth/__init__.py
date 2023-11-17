from fastapi import APIRouter

from . import auth

router = APIRouter(prefix="/auth")

router.include_router(auth.router_auth)
