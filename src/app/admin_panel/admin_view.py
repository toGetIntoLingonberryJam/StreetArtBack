from sqladmin import ModelView

from app.modules.artworks.models.artwork import Artwork
from app.modules.artworks.models.artwork_additions import ArtworkAdditions
from app.modules.artworks.models.artwork_image import ArtworkImage
from app.modules.artworks.models.artwork_location import ArtworkLocation
from app.modules.users.user import User


class UserAdmin(ModelView, model=User):
    column_list = "__all__"


class ArtworkAdmin(ModelView, model=Artwork):
    column_list = "__all__"


class ArtworkAdditionsAdmin(ModelView, model=ArtworkAdditions):
    column_list = "__all__"


class ArtworkImageAdmin(ModelView, model=ArtworkImage):
    column_list = "__all__"


class ArtworkLocationAdmin(ModelView, model=ArtworkLocation):
    column_list = "__all__"