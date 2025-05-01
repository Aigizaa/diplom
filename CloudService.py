import os
import io
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Настройки Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'


class GoogleDriveService:
    def __init__(self, data=None):
        self.data = data  # pandas.DataFrame
        self.service = self._authenticate()

    def _authenticate(self):
        """Авторизация в Google Drive API."""
        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
        return build('drive', 'v3', credentials=creds)

    def load_from_cloud(self, filename='data.xlsx'):
        """Загружает Excel с Google Диска и возвращает DataFrame."""
        try:
            # Поиск файла на Диске
            results = self.service.files().list(
                q=f"name='{filename}'",
                fields="files(id, name)").execute()
            items = results.get('files', [])

            if not items:
                return None, "Файл не найден на Google Диске."

            # Скачивание файла в оперативную память
            file_id = items[0]['id']
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)

            while True:
                status, done = downloader.next_chunk()
                if done:
                    break

            fh.seek(0)
            self.data = pd.read_excel(fh)
            return self.data, None

        except Exception as e:
            return None, f"Ошибка загрузки: {str(e)}"

    def save_to_cloud(self, filename='data.xlsx'):
        """Сохраняет DataFrame в Excel и загружает на Google Диск."""
        if self.data is None:
            return "Нет данных для сохранения."

        temp_file = "temp_dataframe.xlsx"
        try:
            # Сохранение DataFrame во временный файл

            with pd.ExcelWriter(temp_file, engine='openpyxl') as writer:
                self.data.to_excel(writer, index=False)

            # Загрузка на Google Диск
            file_metadata = {'name': filename}
            media = MediaFileUpload(temp_file,
                                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

            # Проверка существования файла
            results = self.service.files().list(
                q=f"name='{filename}'",
                fields="files(id)").execute()
            items = results.get('files', [])

            if items:  # Обновление существующего файла
                file_id = items[0]['id']
                self.service.files().update(
                    fileId=file_id,
                    media_body=media).execute()
                message = f"Файл '{filename}' обновлён."
            else:  # Создание нового файла
                self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id').execute()
                message = f"Файл '{filename}' сохранён на Google Диск."

            os.remove(temp_file)  # Удаление временного файла
            return message

        except Exception as e:
            return f"Ошибка сохранения: {str(e)}"

        finally:
            # Удаляем временный файл, если он существует
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except PermissionError:
                    # Если файл всё ещё занят, игнорируем ошибку (или логируем)
                    pass