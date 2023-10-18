from fastapi import APIRouter

from app.modules.users.schemas import UserRead, UserUpdate
from app.modules.users.fastapi_users_config import fastapi_users

# User Router

user_router = APIRouter(prefix="/user", tags=["user"])

user_router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))
