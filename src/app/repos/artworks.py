from app.modules.artworks.models.artwork import Artwork
from app.repos.SQLAlchemy_repository import SQLAlchemyRepository


class ArtworkRepository(SQLAlchemyRepository):
    model = Artwork

    