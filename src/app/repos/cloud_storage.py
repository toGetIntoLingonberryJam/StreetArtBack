from app.modules.cloud_storage.models import Image
from app.repos.SQLAlchemy_repository import SQLAlchemyRepository


class ImageRepository(SQLAlchemyRepository):
    model = Image
