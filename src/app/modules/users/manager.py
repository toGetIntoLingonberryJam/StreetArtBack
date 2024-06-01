from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin

from app.modules.users.models import User, get_user_db
from app.modules.users.schemas import UserRead
from app.services.cloud_queue import CloudQueueService
from config import settings


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = settings.secret_reset_token
    verification_token_secret = settings.secret_verification_token

    async def on_after_request_verify(
        self, user: UserRead, token: str, request: Optional[Request] = None
    ) -> None:
        print(token)
        CloudQueueService.send_verify_email_to_queue(token, user.email, user.username)

    async def on_after_forgot_password(
        self, user: UserRead, token: str, request: Optional[Request] = None
    ) -> None:
        CloudQueueService.send_reset_password_email_to_queue(token, user.email)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
