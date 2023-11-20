from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin

from app.modules.users.emails.confirm_email import send_verify_email
from app.modules.users.schemas import UserRead
from config import SECRET_RESET_TOKEN, SECRET_VERIFICATION_TOKEN
from app.modules.users.models.user import User, get_user_db


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET_RESET_TOKEN
    verification_token_secret = SECRET_VERIFICATION_TOKEN

    async def on_after_request_verify(
        self, user: UserRead, token: str, request: Optional[Request] = None
    ) -> None:
        status = await send_verify_email(token, user.email, user.username)
        # TODO: logging status


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
