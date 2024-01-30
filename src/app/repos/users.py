from app.modules.artists.models import Artist
from app.modules.moderation.models import Moderator
from app.modules.users.utils.reactions import Reaction
from app.modules.users.models import User
from app.repos.SQLAlchemy_repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    model = User


class ReactionRepository(SQLAlchemyRepository):
    model = Reaction


class ArtistRepository(SQLAlchemyRepository):
    model = Artist


class ModeratorRepository(SQLAlchemyRepository):
    model = Moderator
