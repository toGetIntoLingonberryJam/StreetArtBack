from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Form
from fastapi_users import exceptions
from fastapi_users.router import ErrorCode
from fastapi_users.router.reset import RESET_PASSWORD_RESPONSES
from pydantic import EmailStr
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse

from app.modules.users.utils.forgot_password import get_reset_password_template
from app.modules.users.manager import get_user_manager

password_router = APIRouter()


@password_router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
        request: Request,
        email: EmailStr = Body(..., embed=True),
        user_manager=Depends(get_user_manager)
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
        await user_manager.reset_password(token, password, request)
        return HTTPException(status_code=200, detail={"Успешно изменен пароль."})
    except (
            exceptions.InvalidResetPasswordToken,
            exceptions.UserNotExists,
            exceptions.UserInactive,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
        )
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.RESET_PASSWORD_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )


@password_router.post("/verify_reset_password")
async def reset_password(
        token: Annotated[str, Form()]
):
    return HTMLResponse(content=get_reset_password_template(token), status_code=200)
