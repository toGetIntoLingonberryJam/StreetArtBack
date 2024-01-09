from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin

from app.modules.users.utils.confirm_email import send_verify_email
from app.modules.users.schemas import UserRead
from config import get_settings
from app.modules.users.models import User, get_user_db

from app.modules.users.utils.forgot_password import send_reset_password_email


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = get_settings().secret_reset_token
    verification_token_secret = get_settings().secret_verification_token

    async def on_after_request_verify(
        self, user: UserRead, token: str, request: Optional[Request] = None
    ) -> None:
        print(token)
        await send_verify_email(token, user.email, user.username)

    async def on_after_forgot_password(
        self, user: UserRead, token: str, request: Optional[Request] = None
    ) -> None:
        await send_reset_password_email(token, user.email)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
