from typing import Annotated

from fastapi import Body, Depends, APIRouter, HTTPException, Form
from fastapi_users import exceptions
from fastapi_users.router import ErrorCode
from pydantic import EmailStr
from starlette import status
from starlette.requests import Request

from app.modules.users.manager import get_user_manager
from app.modules.users.schemas import UserRead

verify_router = APIRouter()


@verify_router.post("/request-verify-token", status_code=status.HTTP_202_ACCEPTED)
async def request_verify_token(
    request: Request,
    email: EmailStr = Body(..., embed=True),
    user_manager=Depends(get_user_manager),
):
    try:
        user = await user_manager.get_by_email(email)
        await user_manager.request_verify(user, request)
    except Exception:
        pass

    return None


@verify_router.post("/verify", response_model=UserRead)
async def verify(
    request: Request,
    token: Annotated[str, Form()],
    user_manager=Depends(get_user_manager),
):
    try:
        user = await user_manager.verify(token, request)
        return UserRead.model_validate(user)
    except (exceptions.InvalidVerifyToken, exceptions.UserNotExists):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
        )
    except exceptions.UserAlreadyVerified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.VERIFY_USER_ALREADY_VERIFIED,
        )
