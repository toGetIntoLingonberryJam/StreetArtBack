import asyncio
from typing import Optional
from urllib.parse import urlparse

import imagehash
from botocore.client import BaseClient
from fastapi import UploadFile
from PIL import Image
from boto3 import session
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError

from app.services.cloud_storage import CloudFile
from app.utils.images import generate_blurhash
from config import settings


class CloudObjectStorageService:
    _client: Optional[BaseClient] = None
    _settings = settings
    _chunk_size: int = 1024 * 1024
    _transfer_config: TransferConfig = TransferConfig(multipart_chunksize=_chunk_size)

    @classmethod
    def get_client(cls):
        if CloudObjectStorageService._client is None:
            cls.max_image_size = 1024 * 1024 * 100  # 100 mb
            s3_session = session.Session()
            cls._client = s3_session.client(
                service_name='s3',
                endpoint_url='https://storage.yandexcloud.net',
                aws_access_key_id=cls._settings.aws_access_key_id,
                aws_secret_access_key=cls._settings.aws_secret_access_key,
            )
        return CloudObjectStorageService._client

    @classmethod
    def _get_pressigned_url(cls, client, file_key: str) -> str:
        try:
            response = client.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.bucket_name, 'Key': file_key},
            )
        except ClientError:
            return ""
        return response

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
    def file_exists(cls, file_path: str):
        try:
            client = cls.get_client()
            client.head_object(Bucket=cls._settings.bucket_name, Key=file_path)
            print(f"Файл с ключом '{file_path}' существует.")
            return True
        except ClientError as e:
            print(f"Файл с ключом '{file_path}' не существует.")
            return False

    @classmethod
    async def _upload_file_to_yandex_disk(
            cls,
            client,
            unique_filename: str,
            custom_folder: str,
            image: UploadFile | None = None,
    ) -> CloudFile | None:
        """Загружает файл на Яндекс.Диск. Возвращает публичную ссылку загруженного файла."""
        # Создание правильного пути до выбранной папки загрузки файла в Яндекс.Диск
        custom_folder = (
            ""
            if custom_folder is None or custom_folder == ""
            else f'/{custom_folder.strip("/")}/'
        )
        file_cloud_path = (
                custom_folder + unique_filename
        )

        if image:
            if cls.file_exists(file_cloud_path):
                file_metadata = client.head_object(Bucket=cls._settings.bucket_name, Key=file_cloud_path)
                file_size = file_metadata['ContentLength']
                if file_size < image.size:
                    image.file.seek(0)
                    client.put_object(Body=open(file_cloud_path, 'rb'), Bucket=cls._settings.bucket_name,
                                      Key=file_cloud_path)
            else:
                image.file.seek(0)
                client.upload_fileobj(
                    image.file,
                    cls._settings.bucket_name,
                    file_cloud_path,
                    Config=cls._transfer_config,
                )

        blurhash_value: Optional[str] = await generate_blurhash(
            image_source=image,
            image_url=cls._get_pressigned_url(client=client, file_key=file_cloud_path),
        )

        cloud_file = CloudFile(
            public_url=cls._get_pressigned_url(client=client, file_key=file_cloud_path),
            public_key=file_cloud_path,
            file_path=file_cloud_path,
            blurhash=blurhash_value,
        )

        return cloud_file

    @classmethod
    async def upload_to_yandex_disk(
            cls,
            image: UploadFile | None = None,
            custom_folder: str | None = None,
    ) -> CloudFile | None:
        """Загружает файл на диск или по ссылке. Возвращает публичную ссылку загруженного файла."""
        client = cls.get_client()

        if image:
            unique_filename = cls.generate_unique_filename(image)

        else:
            raise ValueError("Необходимо предоставить либо файл, либо URL изображения.")

        return await cls._upload_file_to_yandex_disk(
            client, unique_filename, custom_folder, image=image
        )

    @staticmethod
    async def upload_files_to_yandex_disk(
            images: Optional[list[UploadFile]] = None,
    ) -> list[CloudFile]:
        cloud_files = []

        if images:
            results = await asyncio.gather(
                *[
                    CloudObjectStorageService.upload_to_yandex_disk(image=image)
                    for image in images
                ]
            )
            cloud_files.extend(
                [
                    cloud_file
                    for cloud_file in results
                    if isinstance(cloud_file, CloudFile)
                ]
            )

        unique_cloud_files = {}
        for cloud_file in cloud_files:
            if cloud_file.public_url not in unique_cloud_files:
                unique_cloud_files[cloud_file.public_url] = cloud_file

        return list(unique_cloud_files.values())

    @classmethod
    async def delete_from_yandex_disk(cls, public_url: str):
        try:
            client = cls.get_client()

            # Парсинг публичной ссылки
            parsed_url = urlparse(public_url)
            key = parsed_url.path.lstrip('/')

            # Удаляем файл
            client.delete_object(Bucket=cls._settings.bucket_name, Key=key)
            print(f"File {key} successfully deleted.")
        except ClientError as e:
            print(f"Error deleting file: {e}")
