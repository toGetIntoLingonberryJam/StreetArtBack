import asyncio
import hashlib
import os
from urllib.parse import urlparse

from PIL import Image
import imagehash
import threading
from typing import Optional

import yadisk
from fastapi import UploadFile
from yadisk.objects import (
    AsyncPublicResourceObject,
    AsyncResourceObject,
    AsyncOperationLinkObject,
)

from app.modules import TicketBase, Artwork
from config import settings


class CloudFile:
    public_url: str
    public_key: str
    file_path: str

    @staticmethod
    def generate_file_path_by_class(obj):
        path = settings.yandex_disk_images_folder + "/"
        if issubclass(obj, TicketBase):
            path += "tickets"
        elif issubclass(obj, Artwork):
            path += "artworks"

    def __init__(self, public_url: str, public_key: str, file_path: str):
        self.public_url = public_url
        self.public_key = public_key
        self.file_path = file_path

    def __str__(self):
        return f"public_url: {self.public_url}, file_path: {self.file_path}"


class CloudStorageService:
    _client: Optional[yadisk.AsyncClient] = None
    _lock = threading.Lock()
    _settings = settings

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

    @staticmethod
    def generate_unique_filename_by_url(image_url: str):
        # Вычисляем хеш изображения
        image_url_hash = hashlib.sha256(str.encode(image_url)).hexdigest()
        # Извлекаем оригинальное расширение файла из URL
        _, file_extension = os.path.splitext(urlparse(image_url).path)
        file_extension = file_extension.lower()  # Приводим к нижнему регистру
        # Извлекаем только имя файла без дополнительных параметров
        file_name = os.path.basename(file_extension).split("?")[0]
        # Получаем уникальное имя файла на основе хеша и оригинального расширения
        unique_filename = f"{image_url_hash}{file_name}"
        return unique_filename

    @classmethod
    async def wait_for_operation(cls, operation: AsyncOperationLinkObject):
        client = cls.get_client()

        while True:
            status = await client.get_operation_status(operation.href)

            if status == "success":
                # Действия при успешном завершении операции
                return True
            elif status == "failed":
                # Действия при неудачном завершении операции
                # print("Operation failed.")
                # break
                return False
            elif status == "in-progress":
                # Ожидание с задержкой перед следующей проверкой
                # Асинхронное ожидание 0.5 секунды перед следующей проверкой
                await asyncio.sleep(0.5)
            else:
                # Обработка других возможных статусов
                print(f"Unknown status: {status}")
                return False

    @classmethod
    async def file_exists(cls, file_path: str):
        client = cls.get_client()
        return await client.is_file(file_path)

    @classmethod
    async def get_file_info(cls, path: str) -> AsyncResourceObject:
        client = cls.get_client()
        meta_info = await client.get_meta(path)
        return meta_info

    @classmethod
    async def _get_file_public_url(
        cls, public_meta: AsyncPublicResourceObject | AsyncResourceObject
    ) -> str:
        public_file_url = public_meta.FIELDS.get("public_url")
        return public_file_url

    @classmethod
    async def _get_file_public_key(
        cls, public_meta: AsyncPublicResourceObject | AsyncResourceObject
    ) -> str:
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
            settings.yandex_disk_images_folder + custom_folder + unique_filename
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
    async def upload_to_yandex_disk_by_url(
        cls, image_url: str, custom_folder: str | None = None
    ) -> CloudFile | None:
        """Загружает файл на диск по ссылке. Возвращает публичную ссылку загруженного файла."""
        client = cls.get_client()

        # Вычисляем хеш из ссылки
        # ToDo: Переделать в вычисление хэша файлом (для того, чтобы избежать одинаковых изображений)
        unique_filename = cls.generate_unique_filename_by_url(image_url=image_url)

        # Создание правильного пути до выбранной папки загрузки изображения в Яндекс.Диск
        custom_folder = (
            "/"
            if custom_folder is None or custom_folder == ""
            else f'/{custom_folder.strip("/")}/'
        )

        # ### Загружаем изображение в Яндекс.Диск ###
        file_cloud_path = (
            settings.yandex_disk_images_folder + custom_folder + unique_filename
        )

        if not await cls.file_exists(file_cloud_path):
            operation = await client.upload_url(
                image_url, file_cloud_path, disable_redirects=False
            )

            if not await cls.wait_for_operation(operation):
                return None  # Если не получилось у Яндекса загрузить файл, то вернётся None.
                # Позже можно переделать чтоб мы сами скачивали (вдруг ресурс заблокирован в Яндексе)

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
            file_path = settings.yandex_disk_images_folder + "/" + filename
            # Удаляем файл
            await client.remove(file_path)
            print(f"File {file_path} successfully deleted.")
        except yadisk.exceptions.BadRequestError as e:
            print(f"Error deleting file: {e}")
