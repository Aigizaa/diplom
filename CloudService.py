import os
import io
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from PySide6.QtWidgets import (QInputDialog, QMessageBox, QComboBox, QDialog, QVBoxLayout, QPushButton, QLabel)


# Настройки Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'

class GoogleDriveService:
    def __init__(self, data=None, parent_ui=None):
        self.data = data  # pandas.DataFrame
        self.parent_ui = parent_ui  # Ссылка на главное окно для вызова диалогов
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

    def get_available_files(self):
        """Возвращает список всех Excel-файлов на Google Диске."""
        results = self.service.files().list(
            q="mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'",
            fields="files(id, name)").execute()
        return results.get('files', [])

    def load_from_cloud(self, filename='data.xlsx'):
        """Загружает выбранный файл с Google Диска."""
        files = self.get_available_files()
        if not files:
            return None, "На Google Диске нет файлов."

        # Диалог выбора файла
        dialog = QDialog(self.parent_ui)
        dialog.setWindowTitle("Выберите файл")
        layout = QVBoxLayout()

        combo = QComboBox()
        combo.addItems([file['name'] for file in files])

        btn_ok = QPushButton("Загрузить")
        btn_ok.clicked.connect(dialog.accept)

        layout.addWidget(QLabel("Доступные файлы:"))
        layout.addWidget(combo)
        layout.addWidget(btn_ok)
        dialog.setLayout(layout)

        if dialog.exec() == 1:
            selected_file = files[combo.currentIndex()]
            file_id = selected_file['id']

            # Скачивание файла
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
        else:
            return None, "Загрузка отменена."

    def save_to_cloud(self, filename='data.xlsx'):
        """Сохраняет DataFrame в Excel после ввода названия."""
        if self.data is None:
            return "Нет данных для сохранения."

        while True:
            # Диалог ввода названия файла
            filename, ok = QInputDialog.getText(
                self.parent_ui,
                "Сохранение файла",
                "Введите название файла (без .xlsx):",
                text="data"
            )
            if not ok:
                return "Сохранение отменено."

            filename += ".xlsx"

            # Проверка существования файла
            results = self.service.files().list(
                q=f"name='{filename}'",
                fields="files(id)").execute()
            items = results.get('files', [])

            if items:
                # Запрос на перезапись
                reply = QMessageBox.question(
                    self.parent_ui,
                    "Файл существует",
                    f"Файл '{filename}' уже существует. Перезаписать?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    continue  # Повторяем ввод названия

            # Сохранение файла
            temp_file = "temp_dataframe.xlsx"
            try:
                with pd.ExcelWriter(temp_file, engine='openpyxl') as writer:
                    self.data.to_excel(writer, index=False)

                media = MediaFileUpload(
                    temp_file,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )

                if items:  # Перезапись
                    file_id = items[0]['id']
                    self.service.files().update(
                        fileId=file_id,
                        media_body=media).execute()
                    message = f"Файл '{filename}' перезаписан."
                else:  # Новый файл
                    file_metadata = {'name': filename}
                    self.service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id').execute()
                    message = f"Файл '{filename}' сохранён."

                return message

            except Exception as e:
                return f"Ошибка: {str(e)}"

            finally:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except PermissionError:
                        print("Временный файл не был удален")
