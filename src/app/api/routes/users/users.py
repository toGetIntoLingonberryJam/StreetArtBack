from fastapi import APIRouter

from app.modules.users.schemas import UserRead, UserUpdate
from app.modules.users.fastapi_users_config import fastapi_users

# User Router

router_users = APIRouter(tags=["Users"])

router_users.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))
router_users.include_router(fastapi_users.get_verify_router(UserRead))
