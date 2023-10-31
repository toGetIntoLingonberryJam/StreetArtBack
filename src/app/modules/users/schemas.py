from typing import Optional

from fastapi_users import schemas
from fastapi_users.schemas import CreateUpdateDictModel
from pydantic import EmailStr, ConfigDict

from app.modules.users.roles import Role


class UserRead(CreateUpdateDictModel):
    id: int
    username: str
    email: EmailStr
    # role: Role

    model_config = ConfigDict(from_attributes=True)


class UserCreate(CreateUpdateDictModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(schemas.BaseUserUpdate):
    username: Optional[str]
