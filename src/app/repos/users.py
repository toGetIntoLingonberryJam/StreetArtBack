from app.modules.users.models import User
from app.repos.SQLAlchemy_repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    model = User
