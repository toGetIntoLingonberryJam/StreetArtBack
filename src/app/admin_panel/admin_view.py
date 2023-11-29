from sqladmin import ModelView

from app.modules.artworks.models.artwork import Artwork
from app.modules.artworks.models.artwork_additions import ArtworkAdditions
from app.modules.artworks.models.artwork_image import ArtworkImage
from app.modules.artworks.models.artwork_location import ArtworkLocation
from app.modules.artworks.models.artwork_moderation import ArtworkModeration
from app.modules.users.models import User


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

    # form_columns = [Artwork.title]
    # Определяем форматтер для отображения значения связного поля
    column_formatters = {
        Artwork.added_by_user: lambda model, a: f"{model.added_by_user.username} (ID: {model.added_by_user.id})",
        Artwork.artist: lambda model, a: f"{model.artist.username} (ID: {model.artist.id})",
        Artwork.location: lambda model, a: f"lat: {model.location.latitude}\nlng: {model.location.longitude}",
        Artwork.images: lambda model, a: f"{len(model.images)}",
        Artwork.moderation: lambda model, a: f"Status: {model.moderation.status.name}"
    }
    # column_formatters = {
    #     'added_by_user': lambda v, c: f"{v.added_by_user.username} (ID: {v.added_by_user.id})"
    # }

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
