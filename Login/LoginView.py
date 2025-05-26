import os
import sys

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                               QPushButton, QFormLayout)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt

def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсу """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class LoginView(QDialog):
    def __init__(self):
        super().__init__()
        # Основные визуальные компоненты
        self.login_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.btn_login = QPushButton("Войти")
        self.init_ui()

    def get_login_and_password(self) -> tuple[str, str]:
        return self.login_edit.text().strip(), self.password_edit.text().strip()

    def init_ui(self):
        self.setWindowTitle("Авторизация")
        icon_path = resource_path("resources/icon2.png")
        self.setWindowIcon(QIcon(icon_path))
        layout = QVBoxLayout()
        self.setFixedSize(450, 550)
        layout.setContentsMargins(30, 30, 30, 30)
        icon_label = QLabel()
        try:
            icon_path = resource_path("resources/icon.png")
            icon_pixmap = QPixmap(icon_path).scaled(
                200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(icon_pixmap)
        except Exception as e:
            print(f"Ошибка загрузки иконки: {str(e)}")
            icon_label.setText("Иконка приложения")
            icon_label.setStyleSheet("font-size: 24px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Название приложения
        title_label = QLabel("Платформа для анализа \nбиомедицинских данных \nMedicalAnalyzer")
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)

        # Форма ввода
        form_layout = QFormLayout()

        # Поле для логина
        self.login_edit.setPlaceholderText("Введите логин")
        self.login_edit.setStyleSheet("""
            padding: 8px;
            font-size: 14px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
        """)
        form_layout.addRow("Логин:", self.login_edit)

        # Поле для пароля
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
        self.btn_login.setStyleSheet("""
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
        layout.addWidget(self.btn_login)
        layout.addStretch()

        # Стиль окна
        self.setStyleSheet("""
            QDialog {
                background-color: #f9f9f9;
                font-family: Arial;
            }
        """)
        self.setLayout(layout)
