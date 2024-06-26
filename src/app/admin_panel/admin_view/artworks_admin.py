from sqladmin import ModelView

from app.modules.artworks.models.artwork import Artwork
from app.modules.artworks.models.artwork_location import ArtworkLocation
from app.modules.images.models.image_artwork import ImageArtwork

DROPDOWN_CATEGORY = "Арт-объект"


class ArtworkAdmin(ModelView, model=Artwork):
    column_list = "__all__"
    DROPDOWN_CATEGORY = DROPDOWN_CATEGORY

    # form_columns = [Artwork.title]
    # Определяем форматтер для отображения значения связного поля
    # column_formatters = {
    #     Artwork.added_by_user: lambda model, a: f"{model.added_by_user.username} (ID: {model.added_by_user.id})",
    #     Artwork.artist: lambda model, a: f"{model.artist.username} (ID: {model.artist.id})",
    #     Artwork.location: lambda model, a: f"lat: {model.location.latitude}\nlng: {model.location.longitude}",
    #     Artwork.images: lambda model, a: f"{len(model.images)}",
    # }
    # column_formatters = {
    #     'added_by_user': lambda v, c: f"{v.added_by_user.username} (ID: {v.added_by_user.id})"
    # }


class ImageArtworkAdmin(ModelView, model=ImageArtwork):
    column_list = "__all__"
    DROPDOWN_CATEGORY = DROPDOWN_CATEGORY


class ArtworkLocationAdmin(ModelView, model=ArtworkLocation):
    column_list = "__all__"
    DROPDOWN_CATEGORY = DROPDOWN_CATEGORY
