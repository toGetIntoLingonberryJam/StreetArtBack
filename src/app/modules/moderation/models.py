from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Moderator(Base):
    __tablename__ = "moderator"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), index=True)

    # requests = relationship(Req)

# get_current_moderator = get_current_moderator