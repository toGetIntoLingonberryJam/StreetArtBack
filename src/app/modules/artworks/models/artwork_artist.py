# from sqlalchemy import Integer, ForeignKey
# from sqlalchemy.orm import Mapped, mapped_column
#
# from app.db import Base
#
#
# class ArtworkAssignee(Base):
#     __tablename__ = "artwork_assignee"
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     artist_id: Mapped[int] = mapped_column(ForeignKey("artist.id"))
#     artwork_id: Mapped[int] = mapped_column(
#         Integer, ForeignKey("artwork.id"), index=True, nullable=True
#     )