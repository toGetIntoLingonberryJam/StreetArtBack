from sqladmin import ModelView


from app.modules.cloud_storage.models import Image

DROPDOWN_CATEGORY = "Изображения"


class ImageAdmin(ModelView, model=Image):
    column_list = "__all__"
    category = DROPDOWN_CATEGORY
