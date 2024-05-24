import re
from typing import List, TypeVar

from fastapi import FastAPI, HTTPException, UploadFile, status
from fastapi.routing import APIRoute, APIRouter
from PIL import Image

from app.api.routes.common import ErrorCode, generate_detail

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


def raise_if_not_image(images: List[UploadFile]):
    """Выбрасывает HTTPException, если хотя бы один файл не является разрешённым изображением"""
    for image in images:
        if not is_image(image):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=generate_detail(
                    error_code=ErrorCode.INVALID_IMAGE_FILE_EXTENSION,
                    message="Invalid image file extension",
                    data={"filename": image.filename},
                ),
            )


def raise_if_not_contains_urls(images_urls: List[str]):
    """Выбрасывает HTTPException, если хотя бы одна строка в списке не содержит URL-адреса."""
    url_pattern = re.compile(r"https?://\S+", re.IGNORECASE)  # Регулярка для http/https
    for url in images_urls:
        if not url_pattern.search(url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid URL: {url}",
            )
