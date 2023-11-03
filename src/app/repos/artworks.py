from app.modules.artworks.models.artwork import Artwork
from app.modules.artworks.models.artwork_image import ArtworkImage
from app.modules.artworks.models.artwork_location import ArtworkLocation
from app.repos.SQLAlchemy_repository import SQLAlchemyRepository


class ArtworkRepository(SQLAlchemyRepository):
    model = Artwork


class ArtworkLocationRepository(SQLAlchemyRepository):
    model = ArtworkLocation


class ArtworkImageRepository(SQLAlchemyRepository):
    model = ArtworkImage
