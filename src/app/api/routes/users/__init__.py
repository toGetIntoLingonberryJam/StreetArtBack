from fastapi import APIRouter

from .forgot_password import password_router
from .user_settings import settings_router
from .verify_user import verify_router

router = APIRouter(prefix="/users", tags=["Users"])

router.include_router(settings_router)
router.include_router(verify_router)
router.include_router(password_router)

