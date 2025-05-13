import os
import io
import pandas as pd
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from PySide6.QtWidgets import (QInputDialog, QMessageBox, QComboBox, QDialog, QVBoxLayout, QPushButton, QLabel)
import socket
import requests
from urllib.request import urlopen
from urllib.error import URLError


# Настройки Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'


class GoogleDriveService:
    def __init__(self, data=None, parent_ui=None):
        self.data = data  # pandas.DataFrame
        self.parent_ui = parent_ui  # Ссылка на главное окно для вызова диалогов
        self.service = self._authenticate()

    def _check_internet_connection(self, timeout=3):
        """Проверяет наличие интернет-соединения."""
        try:
            # Попытка подключения к DNS Google
            socket.create_connection(("8.8.8.8", 53), timeout=timeout)
            return True
        except OSError:
            pass
        try:
            # Альтернативная проверка через HTTP-запрос
            urlopen("https://www.google.com", timeout=timeout)
            return True
        except URLError:
            pass

        return False
        
    def _authenticate(self):
        """Авторизация в Google Drive API с автоматическим обновлением токена."""
        # Сначала проверяем подключение к Интернету
        if not self._check_internet_connection():
            QMessageBox.critical(self.parent_ui, "Ошибка", "Нет подключения к сети Интернет!")
            return None

        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        # Если токен недействителен или истек, обновляем его
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Ошибка при обновлении токена: {e}")
                    if not self._check_internet_connection():
                        QMessageBox.critical(self.parent_ui, "Ошибка", "Нет подключения к сети Интернет!")
                        return None
                    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                    creds = flow.run_local_server(port=0)
            else:
                if not self._check_internet_connection():
                    QMessageBox.critical(self.parent_ui, "Ошибка", "Нет подключения к сети Интернет!")
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)

            # Сохраняем обновленный токен
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())

        return build('drive', 'v3', credentials=creds)

    def _check_and_refresh_token(self):
        """Проверяет и обновляет токен при необходимости."""
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    with open(TOKEN_FILE, 'w') as token:
                        token.write(creds.to_json())
                    self.service = build('drive', 'v3', credentials=creds)
                except Exception as e:
                    print(f"Ошибка при обновлении токена: {e}")
                    self.service = self._authenticate()

    def get_available_files(self):
        """Возвращает список всех Excel-файлов на Google Диске."""
        if not self._check_internet_connection():
            raise Exception("Нет подключения")

        try:
            self._check_and_refresh_token()
            if not self.service:
                return []

            results = self.service.files().list(
                q="mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'",
                fields="files(id, name)").execute()
            return results.get('files', [])
        except Exception as e:
            QMessageBox.critical(self.parent_ui, "Ошибка", f"Ошибка при получении файлов: {e}")
            return []

    def load_from_cloud(self):
        """Загружает выбранный файл с Google Диска."""
        files = self.get_available_files()
        if not files:
            return None, None, "На Google Диске нет файлов."

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
            return self.data, selected_file, None
        else:
            return None, None, "Загрузка отменена."

    def save_to_cloud(self, current_user: str):
        """Сохраняет DataFrame в Excel после ввода названия."""
        if not self._check_internet_connection():
            return "Нет подключения!"
            
        if self.data is None:
            return "Нет данных для сохранения."

        while True:
            # Диалог ввода названия файла
            filename, ok = QInputDialog.getText(
                self.parent_ui,
                "Сохранение файла",
                "Введите название файла (без .xlsx):",
                text="data_"+current_user
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

            try:
                temp_file = "temp_dataframe.xlsx"
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

                try:
                    os.remove(temp_file)
                except PermissionError:
                    print("Временный файл не был удален")

                return message

            except Exception as e:
                return f"Ошибка: {str(e)}"
