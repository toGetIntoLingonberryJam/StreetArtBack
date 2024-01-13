from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import InvalidPasswordException
from fastapi_users.exceptions import UserNotExists
from starlette import status
from starlette.requests import Request

from app.modules.users.fastapi_users_config import current_user
from app.modules.users.manager import UserManager, get_user_manager
from app.modules.users.models import User
from app.modules.users.schemas import (
    UserRead,
    UserUpdatePassword,
    UserUpdate,
    UserUpdateUsername,
)
from app.services.user import UserService
from app.utils.dependencies import UOWDep

settings_router = APIRouter()


@settings_router.get("/me", response_model=UserRead)
def get_user_me(user: User = Depends(current_user)):
    return UserRead.model_validate(user)


@settings_router.delete("/me")
async def delete_user(
    request: Request,
    password: str,
    user=Depends(current_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    credentials = OAuth2PasswordRequestForm(username=user.email, password=password)
    user = await user_manager.authenticate(credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"reason": "invalid password"},
        )
    await user_manager.delete(user, request=request)
    return None


@settings_router.patch("/me/change_password", response_model=UserRead)
async def update_password(
    request: Request,
    user_update: UserUpdatePassword,
    user: User = Depends(current_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    try:
        credentials = OAuth2PasswordRequestForm(
            username=user.email, password=user_update.password
        )
        user = await user_manager.authenticate(credentials)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"reason": "invalid password"},
            )
        updated_user = await user_manager.update(
            UserUpdate(password=user_update.new_password),
            user,
            safe=True,
            request=request,
        )
        return UserRead.model_validate(updated_user)
    except InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"reason": e.reason}
        )


@settings_router.patch("/me/change_username", response_model=UserRead)
async def update_username(
    request: Request,
    user_update: UserUpdateUsername,
    user: User = Depends(current_user),
    user_manager: UserManager = Depends(get_user_manager),
):
    try:
        updated_user = await user_manager.update(
            UserUpdate(username=user_update.new_username),
            user,
            safe=True,
            request=request,
        )
        return UserRead.model_validate(updated_user)
    except InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"reason": e.reason}
        )


@settings_router.get("/user/{user_id}", response_model=UserRead)
async def get_user_by_id(
    user_id: int,
    user_manager: UserManager = Depends(get_user_manager),
):
    try:
        user = await user_manager.get(id=user_id)
        return UserRead.model_validate(user)
    except UserNotExists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"reason": "Пользователь не найден."},
        )
