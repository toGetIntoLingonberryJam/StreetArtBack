from app.modules.artworks.models import Artwork, ArtworkLocation, ArtworkModeration
from app.modules.festivals.models import Festival
from app.repos.SQLAlchemy_repository import SQLAlchemyRepository


class ArtworkRepository(SQLAlchemyRepository):
    model = Artwork


class ArtworkLocationRepository(SQLAlchemyRepository):
    model = ArtworkLocation


class ArtworkModerationRepository(SQLAlchemyRepository):
    model = ArtworkModeration


class FestivalRepository(SQLAlchemyRepository):
    model = Festival
