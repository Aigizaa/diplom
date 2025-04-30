from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PySide6.QtGui import QIcon, QPixmap, QGuiApplication
from PySide6.QtCore import Qt
import os
import sys
# 4. Диалоговые окна
class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")
        self.setFixedSize(500, 550)
        self.move(QGuiApplication.primaryScreen().availableGeometry().center() - self.rect().center())

        icon_path = resource_path("resources/icon2.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)  # Отступы по краям

        # Большая иконка приложения
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
        title_label = QLabel("Анализатор биомедицинских данных")
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
                Программа для анализа клинических показателей пациентов<br>
                с возможностью визуализации данных и статистического анализа
            </p>
            <p style='text-align: center; font-size: 12px; color: #7f8c8d; margin-top: 10px;'>
                Версия 1.0<br>
                Для доступа введите пароль
            </p>
        """)
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)

        # Поля для ввода
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Введите пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet("""
            padding: 8px;
            font-size: 14px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
        """)

        # Кнопка входа
        btn_login = QPushButton("Войти")
        btn_login.clicked.connect(self.verify_password)
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
        layout.addWidget(self.password_edit)
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

    def verify_password(self):
        """Проверка пароля"""
        password = self.password_edit.text()
        if password == "a":
            self.accept()
        elif password == "b":
            self.accept()
        elif password == "c":
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный пароль!")
            self.password_edit.clear()

def resource_path(relative_path):
    """Получение абсолютного пути к ресурсам"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))

    path = os.path.join(base_path, relative_path)
    return path