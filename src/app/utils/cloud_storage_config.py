from PIL import Image
from fastapi import UploadFile

from config import get_settings
import yadisk
import imagehash

# ToDo: возможно стоит вынести инициализацию в app.py
# Инициализация YaDisk
client = yadisk.AsyncClient(token=get_settings().yandex_disk_token)


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


async def upload_to_yandex_disk(image: UploadFile, custom_folder: str | None = None):
    """Загружает файл на диск. Возвращает публичную ссылку загруженного файла."""

    # Открываем изображение и вычисляем хеш
    unique_filename = generate_unique_filename(image)

    # TODO: Проработать все случаи:
    #  нахождение одинаковых файлов для записи в артворк их ссылок;
    #  удаление изображений в методе удаления артворка
    # Создание правильного пути до выбранной папки загрузки изображения в Яндекс.Диск
    custom_folder = '/' if custom_folder is None or custom_folder == '' else f'/{custom_folder.strip("/")}/'

    # Загружаем изображение в Яндекс.Диск
    file_cloud_path = get_settings().yandex_disk_images_folder + custom_folder + unique_filename

    if await client.is_file(file_cloud_path):
        # Получаем информацию о файле
        file_info = await client.get_meta(file_cloud_path)

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
    # public_file = await client.publish(file_cloud_path)
    await client.publish(file_cloud_path)
    public_file_info = await client.get_meta(file_cloud_path)

    # Получение ранее созданной публичной ссылки
    public_file_url = public_file_info.FIELDS.get("public_url")

    return public_file_url


async def delete_from_yandex_disk(public_url: str):
    try:
        # Получаем информацию о файле по публичной ссылке
        meta_info = await client.get_public_meta(public_url)

        # Получаем путь к файлу на Яндекс.Диске
        filename = meta_info.FIELDS.get("name")

        file_path = get_settings().yandex_disk_images_folder + "/" + filename

        # Удаляем файл
        await client.remove(file_path)
        print(f"Файл {file_path} успешно удален.")
    except yadisk.exceptions.BadRequestError as e:
        print(f"Ошибка при удалении файла: {e}")
