from fastapi import APIRouter, Depends

from app.modules.users.schemas import UserRead, UserUpdate
from app.modules.users.user import User
from app.modules.users.fastapi_users_config import fastapi_users, current_user

# User Router

user_router = APIRouter(prefix="/user", tags=["user"])

user_router.include_router(fastapi_users.get_users_router(UserRead, UserUpdate))

# Почему-то current_user не возвращает то, что должен. Только лишь 403 Forbidden
# @user_router.get("/protected-hello-route")
# def protected_route(user: User = Depends(current_user)):
#     return f"Hello, {user.username}"
