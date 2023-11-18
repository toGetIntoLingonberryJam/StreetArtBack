from fastapi import APIRouter

from app.api.routes.users.routes import router
from app.modules.users.schemas import UserRead
from app.modules.users.fastapi_users_config import fastapi_users

# User Router

router_users = APIRouter(tags=["Users"])

router_users.include_router(router)
router_users.include_router(fastapi_users.get_verify_router(UserRead))
router_users.include_router(fastapi_users.get_reset_password_router())
