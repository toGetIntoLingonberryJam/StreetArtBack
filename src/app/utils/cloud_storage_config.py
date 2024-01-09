from PIL import Image
from fastapi import UploadFile

from config import get_settings
import yadisk
import imagehash

# ToDo: возможно стоит вынести инициализацию в app.py
# Инициализация YaDisk
y = yadisk.YaDisk(token=get_settings().yandex_disk_token)


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


async def upload_to_yandex_disk(image: UploadFile):
    """Загружает файл на диск. Возвращает публичную ссылку загруженного файла."""

    # Открываем изображение и вычисляем хеш
    unique_filename = generate_unique_filename(image)

    # Загружаем изображение в Яндекс.Диск
    file_cloud_path = get_settings().yandex_disk_images_folder + "/" + unique_filename

    if y.is_file(file_cloud_path):
        # Получаем информацию о файле
        file_info = y.get_meta(file_cloud_path)

        # Проверяем размер текущего файла на диске и нового изображения
        if file_info["size"] < image.size:
            # Размер нового изображения больше, заменяем файл на диске
            image.file.seek(0)
            y.upload(image.file, file_cloud_path, overwrite=True)
    else:
        # Файл не найден, загружаем новый
        image.file.seek(0)
        y.upload(image.file, file_cloud_path)

    # Предоставление общего доступа к файлу
    public_file = y.publish(file_cloud_path)

    # Получение ранее полученной публичной ссылки
    file_public_url = public_file.get_meta().FIELDS.get("public_url")

    return file_public_url


async def delete_from_yandex_disk(public_url: str):
    try:
        # Получаем информацию о файле по публичной ссылке
        meta_info = y.get_public_meta(public_url)

        # Получаем путь к файлу на Яндекс.Диске
        filename = meta_info.FIELDS.get("name")

        file_path = get_settings().yandex_disk_images_folder + "/" + filename

        # Удаляем файл
        y.remove(file_path)
        print(f"Файл {file_path} успешно удален.")
    except yadisk.exceptions.BadRequestError as e:
        print(f"Ошибка при удалении файла: {e}")
