from sqladmin import ModelView

from app.modules.models import Artist, Moderator, User

DROPDOWN_CATEGORY = "Аккаунт"


class UserAdmin(ModelView, model=User):
    column_list = "__all__"
    # column_labels = {User.added_artworks: "объекты пользователя"}

    category = DROPDOWN_CATEGORY

    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"


class ArtistAdmin(ModelView, model=Artist):
    column_list = "__all__"
    # column_labels = {User.added_artworks: "объекты пользователя"}

    category = DROPDOWN_CATEGORY

    name = "Художник"
    name_plural = "Художники"


class ModeratorAdmin(ModelView, model=Moderator):
    column_list = "__all__"
    # column_labels = {User.added_artworks: "объекты пользователя"}

    category = DROPDOWN_CATEGORY

    name = "Модератор"
    name_plural = "Модераторы"
