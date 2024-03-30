from app.modules.artists.models.artist import Artist
from app.modules.moderation.models import Moderator
from app.modules.users.models import User
from app.repos.SQLAlchemy_repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    model = User


class ArtistRepository(SQLAlchemyRepository):
    model = Artist


class ModeratorRepository(SQLAlchemyRepository):
    model = Moderator
