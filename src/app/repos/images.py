from app.modules.images.models import Image, ImageArtwork, ImageTicket
from app.repos.SQLAlchemy_repository import SQLAlchemyRepository


class ImageArtworkRepository(SQLAlchemyRepository):
    model = ImageArtwork


class ImageTicketRepository(SQLAlchemyRepository):
    model = ImageTicket


class ImageRepository(SQLAlchemyRepository):
    model = Image
