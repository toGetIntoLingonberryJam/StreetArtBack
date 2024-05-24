import io
from typing import Optional, Union

from blurhash import blurhash
import httpx
import numpy
from PIL import Image
from fastapi import UploadFile

from config import settings


async def generate_blurhash(
    image_source: Optional[Union[UploadFile, bytes, str]] = None,
    image_url: Optional[str] = None,
) -> Optional[str]:
    """
    Генерирует BlurHash изображения из различных источников.

    Args:
        image_source: Объект файла изображения (например, UploadFile).
        image_url: URL изображения.

    Returns:
       Строка BlurHash или None, если генерация BlurHash не удалась.
    """
    try:
        if image_source:
            image_source.file.seek(0)
            pil_image = Image.open(image_source.file)
        elif image_url:
            async with (
                httpx.AsyncClient() as client
            ):  # Используем httpx для асинхронного запроса
                client.headers = {"Authorization": "OAuth " + settings.yandex_disk_token}
                response = await client.get(image_url)
                response.raise_for_status()
                pil_image = Image.open(io.BytesIO(response.content))
        else:
            return None

        # Генерация BlurHash вне зависимости от источника изображения
        np_array_image = numpy.array(pil_image)
        blurhash_image = blurhash.blurhash_encode(np_array_image)

    except (IOError, ValueError, httpx.HTTPError) as e:
        print(f"Ошибка при генерации BlurHash: {e}")
        return None  # Возвращаем None в случае ошибки

    return blurhash_image
