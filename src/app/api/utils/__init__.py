from typing import TypeVar

from PIL import Image
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
    try:
        with Image.open(file.file) as img:
            img.verify()
            return True
    except (IOError, SyntaxError):
        return False
