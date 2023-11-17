from sqladmin import ModelView

from app.modules.artworks.models.artwork import Artwork
from app.modules.artworks.models.artwork_additions import ArtworkAdditions
from app.modules.artworks.models.artwork_image import ArtworkImage
from app.modules.artworks.models.artwork_location import ArtworkLocation
from app.modules.artworks.models.artwork_moderation import ArtworkModeration
from app.modules.users.user import User


class UserAdmin(ModelView, model=User):
    column_list = "__all__"
    column_labels = {User.added_artworks: "объекты пользователя"}

    category = "Аккаунт"

    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"



class ArtworkAdmin(ModelView, model=Artwork):
    column_list = "__all__"

    category = "Арт-объект"


class ArtworkAdditionsAdmin(ModelView, model=ArtworkAdditions):
    column_list = "__all__"
    category = "Арт-объект"


class ArtworkImageAdmin(ModelView, model=ArtworkImage):
    column_list = "__all__"
    category = "Арт-объект"


class ArtworkLocationAdmin(ModelView, model=ArtworkLocation):
    column_list = "__all__"
    category = "Арт-объект"


class ArtworkModerationAdmin(ModelView, model=ArtworkModeration):
    column_list = "__all__"
    category = "Арт-объект"
