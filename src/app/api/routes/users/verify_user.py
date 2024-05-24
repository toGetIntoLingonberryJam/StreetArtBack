from fastapi import APIRouter, Body, Depends
from fastapi_users import exceptions
from pydantic import EmailStr
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse

from app.modules.users.manager import get_user_manager
from app.modules.users.schemas import UserRead
from app.modules.users.utils.confirm_email import get_result_template

verify_router = APIRouter()


@verify_router.post(
    "/request-verify-token", status_code=status.HTTP_202_ACCEPTED, tags=["verify-front"]
)
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


@verify_router.get("/verify", tags=["verify-back"])
async def verify(
    token: str,
    request: Request,
    user_manager=Depends(get_user_manager),
):
    try:
        await user_manager.verify(token, request)
        return HTMLResponse(content=get_result_template(True), status_code=200)
    except (exceptions.InvalidVerifyToken, exceptions.UserNotExists):
        return HTMLResponse(content=get_result_template(False), status_code=400)
    except exceptions.UserAlreadyVerified:
        return HTMLResponse(content=get_result_template(True), status_code=200)
