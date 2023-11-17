from fastapi import APIRouter

from . import users

router = APIRouter(prefix="/users")

router.include_router(users.router_users)
