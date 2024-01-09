import asyncio

from PIL import Image
import imagehash
import threading
from typing import Optional

import yadisk
from fastapi import UploadFile
from yadisk.objects import AsyncPublicResourceObject

from app.modules import TicketBase, Artwork
from config import get_settings


class CloudFile:
    public_url: str
    public_key: str
    file_path: str

    @staticmethod
    def generate_file_path_by_class(obj):
        path = get_settings().yandex_disk_images_folder + "/"
        if issubclass(obj, TicketBase):
            path += "tickets"
        elif issubclass(obj, Artwork):
            path += "artworks"

    def __init__(self, public_url: str, public_key: str, file_path: str):
        self.public_url = public_url
        self.public_key = public_key
        self.file_path = file_path


class CloudStorageService:
    _client: Optional[yadisk.AsyncClient] = None
    _lock = threading.Lock()
    _settings = get_settings()

    @classmethod
    def get_client(cls):
        if CloudStorageService._client is None:
            with CloudStorageService._lock:
                if CloudStorageService._client is None:
                    CloudStorageService._client = yadisk.AsyncClient(
                        token=cls._settings.yandex_disk_token
                    )
        return CloudStorageService._client

    @staticmethod
    def generate_unique_filename(image: UploadFile):
        # Открываем изображение
        img = Image.open(image.file)
        # Вычисляем хеш изображения
        img_hash = imagehash.average_hash(img)
        # Получаем оригинальное расширение файла
        file_extension = "." + image.filename.rsplit(".", 1)[-1]
        # Получаем уникальное имя файла на основе хеша и оригинального расширения
        unique_filename = f"{img_hash}{file_extension}"
        return unique_filename

    @classmethod
    async def file_exists(cls, file_path: str):
        client = cls.get_client()
        return await client.is_file(file_path)

    @classmethod
    async def get_file_info(cls, path: str) -> AsyncPublicResourceObject:
        client = cls.get_client()
        meta_info = await client.get_meta(path)
        return meta_info

    @classmethod
    async def _get_file_public_url(cls, public_meta: AsyncPublicResourceObject) -> str:
        public_file_url = public_meta.FIELDS.get("public_url")
        return public_file_url

    @classmethod
    async def _get_file_public_key(cls, public_meta: AsyncPublicResourceObject) -> str:
        public_file_url = public_meta.FIELDS.get("public_key")
        return public_file_url

    @classmethod
    async def upload_to_yandex_disk(
        cls, image: UploadFile, custom_folder: str | None = None
    ) -> CloudFile:
        """Загружает файл на диск. Возвращает публичную ссылку загруженного файла."""
        client = cls.get_client()
        # Открываем изображение и вычисляем хеш
        unique_filename = cls.generate_unique_filename(image)

        # TODO: Проработать все случаи:
        #  нахождение одинаковых файлов для записи в артворк их ссылок;
        #  удаление изображений в методе удаления артворка
        # Создание правильного пути до выбранной папки загрузки изображения в Яндекс.Диск
        custom_folder = (
            "/"
            if custom_folder is None or custom_folder == ""
            else f'/{custom_folder.strip("/")}/'
        )

        # ### Загружаем изображение в Яндекс.Диск ###
        file_cloud_path = (
            get_settings().yandex_disk_images_folder + custom_folder + unique_filename
        )

        if await cls.file_exists(file_cloud_path):
            # Получаем информацию о файле
            file_info = await cls.get_file_info(file_cloud_path)
            # Проверяем размер текущего файла на диске и нового изображения
            if file_info["size"] < image.size:
                # Размер нового изображения больше, заменяем файл на диске
                image.file.seek(0)
                await client.upload(image.file, file_cloud_path, overwrite=True)
        else:
            # Файл не найден, загружаем новый
            image.file.seek(0)
            await client.upload(image.file, file_cloud_path)

        # Предоставление общего доступа к файлу
        await client.publish(file_cloud_path)

        # Получение ранее созданной публичной ссылки
        public_file_info = await cls.get_file_info(file_cloud_path)

        cloud_file = CloudFile(
            public_url=await cls._get_file_public_url(public_file_info),
            public_key=await cls._get_file_public_key(public_file_info),
            file_path=file_cloud_path,
        )

        return cloud_file

    @classmethod
    async def delete_from_yandex_disk(cls, public_url: str):
        try:
            client = cls.get_client()
            # Получаем информацию о файле по публичной ссылке
            meta_info = await client.get_public_meta(public_url)
            # Получаем путь к файлу на Яндекс.Диске
            filename = meta_info.FIELDS.get("name")
            file_path = get_settings().yandex_disk_images_folder + "/" + filename
            # Удаляем файл
            await client.remove(file_path)
            print(f"File {file_path} successfully deleted.")
        except yadisk.exceptions.BadRequestError as e:
            print(f"Error deleting file: {e}")
