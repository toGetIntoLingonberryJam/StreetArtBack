import io
from typing import Optional, Union
import blurhash  # noqa: lib 'blurhash-python' has the same name as its predecessor - 'blurhash'
import httpx
from PIL import Image
from fastapi import UploadFile
from config import settings
from logger_config import logger


async def generate_blurhash(
    image_source: Optional[Union[UploadFile, bytes, str]] = None,
    image_url: Optional[str] = None,
) -> Optional[str]:
    """
    Генерирует BlurHash изображения из различных источников.

    Args:
        image_source: Объект файла изображения (например, UploadFile), байтовый массив или строка пути.
        image_url: URL изображения.

    Returns:
       Строка BlurHash или None, если генерация BlurHash не удалась.
    """
    pil_image = None

    try:
        if image_source:
            if isinstance(image_source, UploadFile):
                image_source.file.seek(0)
                pil_image = Image.open(image_source.file)
            elif isinstance(image_source, bytes):
                pil_image = Image.open(io.BytesIO(image_source))
            elif isinstance(image_source, str):
                pil_image = Image.open(image_source)
        elif image_url:
            async with httpx.AsyncClient(
                timeout=10
            ) as client:  # Используем httpx для асинхронного запроса
                client.headers = {"Authorization": "OAuth " + settings.yandex_disk_token}
                response = await client.get(image_url)
                response.raise_for_status()
                pil_image = Image.open(io.BytesIO(response.content))
        else:
            return None

        # Генерация BlurHash вне зависимости от источника изображения
        if pil_image:
            pil_image.thumbnail((200, 200))
            blurhash_image = blurhash.encode(
                image=pil_image, x_components=9, y_components=9
            )
        else:
            return None
    except (IOError, ValueError, httpx.HTTPError) as e:
        logger.error(f"Ошибка при генерации BlurHash: {e}")
        return None  # Возвращаем None в случае ошибки

    return blurhash_image
