from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Создание объекта GoogleAuth и авторизация с использованием учетных данных
gauth = GoogleAuth()

gauth.LoadCredentialsFile("streetartback-c8fbaa6b3ed3.json")  # Замените на путь к вашему JSON-файлу

gauth.Authorize()

# gauth.SaveCredentialsFile("path/to/your/credentials.json")  # Сохраните учетные данные для будущего использования

drive = GoogleDrive(gauth)

# Теперь вы авторизованы и можете использовать Google Drive API для загрузки и скачивания файлов.


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
folder_id = "16FqTQxhAbSazJ3GlJSawi8mDYqA3yaaA"  # ID папки, в которую вы хотите загрузить файл
image_path = "static/shakal.jpg"  # Путь к изображению, которое вы хотите загрузить
download_path = "static/image.jpg"  # Путь, по которому вы хотите сохранить скачанное изображение
file_id = "YOUR_FILE_ID"  # ID файла на Google Drive, который вы хотите скачать

# Загрузка изображения
upload_image_to_drive(image_path, folder_id)

# Скачивание изображения
# download_image_from_drive(file_id, download_path)