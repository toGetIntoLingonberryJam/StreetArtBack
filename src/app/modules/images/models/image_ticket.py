from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

# from app.db import Base
from app.modules.images.models import Image
from app.modules.images.utils.classes import ImageModel


class ImageTicket(Image):
    __tablename__ = ImageModel.IMAGE_TICKET.value
    __mapper_args__ = {"polymorphic_identity": ImageModel.IMAGE_TICKET.value}

    id: Mapped[int] = mapped_column(None, ForeignKey("image.id"), primary_key=True)

    # Отношение к объекту TicketBase
    ticket_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("ticket.id", ondelete="CASCADE")
    )

    ticket: Mapped["TicketBase"] = relationship("TicketBase", back_populates="images")
