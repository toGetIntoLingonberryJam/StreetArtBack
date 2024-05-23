from typing import Optional

from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import ConfigDict, EmailStr


class UserRead(CreateUpdateDictModel):
    id: int
    username: str
    email: EmailStr
    is_verified: bool
    is_artist: bool
    is_moderator: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)


class UserCreate(CreateUpdateDictModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(schemas.BaseUserUpdate):
    username: Optional[str] = None


class UserUpdatePassword(CreateUpdateDictModel):
    password: str
    new_password: str


class UserUpdateUsername(CreateUpdateDictModel):
    new_username: str
