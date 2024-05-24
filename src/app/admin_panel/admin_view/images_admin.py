from sqladmin import ModelView

from app.modules.images.models import Image

DROPDOWN_CATEGORY = "Изображения"


class ImageAdmin(ModelView, model=Image):
    column_list = "__all__"
    category = DROPDOWN_CATEGORY
