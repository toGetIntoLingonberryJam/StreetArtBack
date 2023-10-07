from fastapi import Depends
from fastapi_users import BaseUserManager, IntegerIDMixin

from config import SECRET_RESET_TOKEN, SECRET_VERIFICATION_TOKEN
from app.modules.users.user import User, get_user_db


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET_RESET_TOKEN
    verification_token_secret = SECRET_VERIFICATION_TOKEN

    # Todo: переопределить функцию create из BaseUserManager, чтобы урегулировать ID роли при регистрации


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
