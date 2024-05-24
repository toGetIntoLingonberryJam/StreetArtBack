from typing import Annotated

from fastapi import APIRouter, Body, Depends, Form
from fastapi_users import exceptions
from fastapi_users.router.reset import RESET_PASSWORD_RESPONSES
from pydantic import EmailStr
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse

from app.modules.users.manager import get_user_manager
from app.modules.users.utils.forgot_password import (
    get_reset_password_template,
    get_result_password_template,
)

password_router = APIRouter()


@password_router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    request: Request,
    email: EmailStr = Body(..., embed=True),
    user_manager=Depends(get_user_manager),
):
    try:
        user = await user_manager.get_by_email(email)
    except exceptions.UserNotExists:
        return None

    try:
        await user_manager.forgot_password(user, request)
    except exceptions.UserInactive:
        pass

    return None


@password_router.post("/reset-password", responses=RESET_PASSWORD_RESPONSES)
async def reset_password(
    request: Request,
    token: Annotated[str, Form()],
    password: Annotated[str, Form()],
    user_manager=Depends(get_user_manager),
):
    try:
        user = await user_manager.reset_password(token, password, request)
        return HTMLResponse(content=get_result_password_template(True), status_code=200)
    except (
        exceptions.InvalidResetPasswordToken,
        exceptions.UserNotExists,
        exceptions.UserInactive,
        exceptions.InvalidPasswordException,
    ):
        return HTMLResponse(content=get_result_password_template(False), status_code=400)


@password_router.get("/verify_reset_password")
async def get_reset_password_form(token: str):
    return HTMLResponse(content=get_reset_password_template(token), status_code=200)
