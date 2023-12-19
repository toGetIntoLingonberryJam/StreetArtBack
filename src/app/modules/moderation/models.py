from fastapi import Depends, HTTPException
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.modules.users.fastapi_users_config import current_user
from app.modules.users.models import User


class Moderator(Base):
    __tablename__ = "moderator"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)

    # requests = relationship(Req)


# get_current_moderator = get_current_moderator

async def current_artist(user: User = Depends(current_user)):
    if not user.is_artist:
        raise HTTPException(status_code=403, detail="Нет доступа.")
