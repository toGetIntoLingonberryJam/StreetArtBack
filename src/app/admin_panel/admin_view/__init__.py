import sqladmin
from sqladmin.forms import Boolean, ColumnProperty, ModelConverterBase, Union, validators

from app.admin_panel.admin_view.artworks_admin import (
    ArtworkAdmin,
    ArtworkLocationAdmin,
    ImageArtworkAdmin,
)
from app.admin_panel.admin_view.images_admin import ImageAdmin
from app.admin_panel.admin_view.tickets_admin import TicketArtworkAdmin, TicketBaseAdmin
from app.admin_panel.admin_view.users_admin import ArtistAdmin, ModeratorAdmin, UserAdmin


# Переопределяем метод _prepare_column используя подход Monkey Patching
def new_prepare_column(
    self, prop: ColumnProperty, form_include_pk: bool, kwargs: dict
) -> Union[dict, None]:
    """Переопределяет метод _prepare_column класса ModelConverterBase. Для корректного вывода полей, при наследовании"""

    # Проверка версии
    custom_method_lib_version = "0.16.1"
    current_lib_version = sqladmin.__version__
    if custom_method_lib_version not in current_lib_version:
        raise RuntimeError(
            f"Внимание! Метод _prepare_column в библиотеке sqladmin мог быть изменен. "
            f"Пожалуйста, просмотрите код библиотеки и обновите ваш кастомный метод."
        )

    column = prop.columns[0]

    if (column.primary_key or column.foreign_keys) and not form_include_pk:
        return None

    default = getattr(column, "default", None)

    if default is not None:
        # Only actually change default if it has an attribute named
        # 'arg' that's callable.
        callable_default = getattr(default, "arg", None)

        if callable_default is not None:
            # ColumnDefault(val).arg can be also a plain value
            default = (
                callable_default(None) if callable(callable_default) else callable_default
            )

    kwargs["default"] = default
    optional_types = (Boolean,)

    if column.nullable:
        kwargs["validators"].append(validators.Optional())

    if (
        not column.nullable
        and not isinstance(column.type, optional_types)
        and not column.default
        and not column.server_default
    ):
        kwargs["validators"].append(validators.InputRequired())

    return kwargs


# Переопределяем метод в экземпляре класса
ModelConverterBase._prepare_column = new_prepare_column
