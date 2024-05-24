from fastapi import APIRouter

from app.modules.users.auth.auth_config import auth_backend
from app.modules.users.fastapi_users_config import fastapi_users
from app.modules.users.schemas import UserCreate, UserRead

# Auth Router

router_auth = APIRouter(tags=["Auth"])

router_auth.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
router_auth.include_router(fastapi_users.get_auth_router(auth_backend))
