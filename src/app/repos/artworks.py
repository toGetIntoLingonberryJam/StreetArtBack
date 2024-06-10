from app.modules.artworks.models import Artwork, ArtworkLocation
from app.modules.festivals.models import Festival
from app.repos.SQLAlchemy_repository import SQLAlchemyRepository


class ArtworkRepository(SQLAlchemyRepository):
    model = Artwork


class ArtworkLocationRepository(SQLAlchemyRepository):
    model = ArtworkLocation


class FestivalRepository(SQLAlchemyRepository):
    model = Festival
