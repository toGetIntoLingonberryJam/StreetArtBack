from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Авторизация и получение доступа к Google Drive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()  # Откроет окно браузера для аутентификации

drive = GoogleDrive(gauth)

# Загрузка файла в Google Drive
def upload_image_to_drive(image_path, folder_id):
    file = drive.CreateFile({'title': image_path.split("/")[-1], 'parents': [{'id': folder_id}]})
    file.Upload()
    print(f'Файл {file["title"]} успешно загружен на Google Drive')

# Скачивание файла с Google Drive
def download_image_from_drive(file_id, save_path):
    file = drive.CreateFile({'id': file_id})
    file.GetContentFile(save_path)
    print(f'Файл {file["title"]} успешно скачан')

# Замените на свои данные
folder_id = "YOUR_FOLDER_ID"  # ID папки, в которую вы хотите загрузить файл
image_path = "path/to/your/image.jpg"  # Путь к изображению, которое вы хотите загрузить
download_path = "path/to/save/image.jpg"  # Путь, по которому вы хотите сохранить скачанное изображение
file_id = "YOUR_FILE_ID"  # ID файла на Google Drive, который вы хотите скачать

# Загрузка изображения
upload_image_to_drive(image_path, folder_id)

# Скачивание изображения
download_image_from_drive(file_id, download_path)
