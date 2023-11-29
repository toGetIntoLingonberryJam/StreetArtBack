from fastapi import APIRouter
from fastapi_users import fastapi_users

from app.modules.users.manager import get_user_manager
from .user_settings import settings_router
from .verify_user import verify_router

router = APIRouter(prefix="/users", tags=["Users"])

router.include_router(settings_router)
router.include_router(verify_router)
router.include_router(fastapi_users.get_reset_password_router(get_user_manager))

