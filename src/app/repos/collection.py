from app.modules.collections.models import ArtistLike, ArtworkLike, FestivalLike
from app.repos.SQLAlchemy_repository import SQLAlchemyRepository


class ArtworkLikeRepository(SQLAlchemyRepository):
    model = ArtworkLike


class ArtistLikeRepository(SQLAlchemyRepository):
    model = ArtistLike


class FestivalLikeRepository(SQLAlchemyRepository):
    model = FestivalLike
