import imghdr
from typing import TypeVar

from fastapi import FastAPI, UploadFile
from fastapi.routing import APIRoute, APIRouter


ParentT = TypeVar("ParentT", APIRouter, FastAPI)


def remove_trailing_slashes_from_routes(parent: ParentT) -> ParentT:
    """Удаляет конечные слэши со всех маршрутов в данном маршрутизаторе"""

    for route in parent.routes:
        if isinstance(route, APIRoute):
            route.path = route.path.rstrip("/")

    return parent


def is_image(file: UploadFile) -> bool:
    allowed_extensions = {
        "webp",
        "jpg",
        "jpeg",
        "png",
        "heic",
    }  # Расширения файлов изображений, которые разрешены
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        return False

    # Если расширение файла соответствует изображению, дополнительно проверяем его содержимое
    content = file.file.read(
        1024
    )  # Считываем первые 1024 байта для определения типа содержимого
    image_type = imghdr.what(None, h=content)

    return image_type is not None
