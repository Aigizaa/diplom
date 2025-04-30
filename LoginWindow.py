import os
import sys
import pandas as pd
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                               QPushButton, QMessageBox, QFormLayout)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt


def resource_path(relative_path):
    """Получение абсолютного пути к ресурсам"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")
        self.setFixedSize(500, 550)
        self.users_db = None
        self.current_user = None
        self.load_users_db()  # Загружаем базу пользователей
        self.init_ui()
        icon_path = resource_path("resources/icon2.png")
        self.setWindowIcon(QIcon(icon_path))

    def load_users_db(self):
        """Загрузка базы пользователей из Excel файла"""
        try:
            # Путь к файлу с пользователями
            db_path = resource_path("databases/doctors_db.xlsx")

            # Проверяем существование файла
            if not os.path.exists(db_path):
                # Создаем файл с тестовым пользователем, если его нет
                default_users = pd.DataFrame({
                    'ФИО': ['Иванов Иван Иванович'],
                    'Логин': ['admin'],
                    'Пароль': ['admin123']
                })
                default_users.to_excel(db_path, index=False)
                self.users_db = default_users
            else:
                # Читаем существующий файл
                self.users_db = pd.read_excel(db_path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось загрузить базу врачей:\n{str(e)}")
            self.users_db = pd.DataFrame(columns=['ФИО', 'Логин', 'Пароль'])

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        icon_label = QLabel()
        try:
            icon_path = resource_path("resources/icon.png")
            icon_pixmap = QPixmap(icon_path).scaled(
                200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(icon_pixmap)
        except Exception as e:
            print(f"Ошибка загрузки иконки: {str(e)}")
            icon_label.setText("Иконка приложения")
            icon_label.setStyleSheet("font-size: 24px;")
        icon_label.setAlignment(Qt.AlignCenter)

        # Название приложения
        title_label = QLabel("Медицинский анализатор данных")
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)

        # Описание приложения
        description = QLabel("""
            <p style='text-align: center; font-size: 14px; color: #34495e;'>
                Профессиональная система анализа медицинских данных
            </p>
            <p style='text-align: center; font-size: 12px; color: #7f8c8d; margin-top: 10px;'>
                Версия 2.0<br>
                Для доступа введите учетные данные
            </p>
        """)
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)

        # Форма ввода
        form_layout = QFormLayout()

        # Поле для логина
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Введите логин")
        self.login_edit.setStyleSheet("""
            padding: 8px;
            font-size: 14px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
        """)
        form_layout.addRow("Логин:", self.login_edit)

        # Поле для пароля
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Введите пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet("""
            padding: 8px;
            font-size: 14px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
        """)
        form_layout.addRow("Пароль:", self.password_edit)

        # Кнопка входа
        btn_login = QPushButton("Войти")
        btn_login.clicked.connect(self.verify_credentials)
        btn_login.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        layout.addSpacing(10)
        layout.addWidget(icon_label)
        layout.addSpacing(10)
        layout.addWidget(title_label)
        layout.addWidget(description)
        layout.addSpacing(20)
        layout.addLayout(form_layout)
        layout.addSpacing(10)
        layout.addWidget(btn_login)
        layout.addStretch()

        # Стиль окна
        self.setStyleSheet("""
            QDialog {
                background-color: #f9f9f9;
                font-family: Arial;
            }
        """)
        self.setLayout(layout)

    def verify_credentials(self):
        """Проверка логина и пароля"""
        login = self.login_edit.text().strip()
        password = self.password_edit.text().strip()
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль!")
            return
        try:
            # Ищем пользователя в базе
            user = self.users_db[
                (self.users_db['Логин'] == login) &
                (self.users_db['Пароль'] == password)
                ]

            if not user.empty:
                # Сохраняем информацию о пользователе
                self.current_user = {
                    'ФИО': user.iloc[0]['ФИО'],
                    'Логин': login
                }
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")
                self.password_edit.clear()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Ошибка проверки учетных данных:\n{str(e)}")