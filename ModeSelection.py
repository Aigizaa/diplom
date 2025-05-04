import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                               QPushButton, QSpacerItem, QSizePolicy)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt


class ModeSelectionView(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.btn_create = QPushButton("Создание и пополнение")
        self.btn_analyze = QPushButton("Анализ")
        self.init_ui()

    def init_ui(self):
        icon_path = os.path.abspath("resources/icon.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Выбор режима работы")
        self.setFixedSize(750, 550)

        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 30, 50, 30)
        main_layout.setSpacing(5)

        # Иконка приложения
        icon_label = QLabel()
        try:
            icon_path = os.path.abspath("resources/icon.png")
            icon_pixmap = QPixmap(icon_path).scaled(
                170, 170, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(icon_pixmap)
        except Exception as e:
            print(f"Ошибка загрузки иконки: {str(e)}")
            icon_label.setText("Иконка приложения")
            icon_label.setStyleSheet("font-size: 24px;")
        icon_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(icon_label)
        main_layout.addSpacing(50)

        # Надпись по центру
        label = QLabel("Выберите режим работы")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
            }
        """)
        main_layout.addWidget(label)

        # Информация о пользователе
        user_label = QLabel(f"Вы вошли как: {self.current_user['ФИО']}")
        user_label.setAlignment(Qt.AlignCenter)
        user_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #7f8c8d;
                margin-bottom: 15px;
            }
        """)
        main_layout.addWidget(user_label)

        # Добавляем вертикальный отступ перед кнопками
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Кнопка "Создание"
        self.btn_create.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                border-radius: 5px;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        main_layout.addWidget(self.btn_create, 0, Qt.AlignCenter)

        # Отступ между кнопками
        main_layout.addSpacing(20)

        # Кнопка "Анализ"

        self.btn_analyze.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                border-radius: 5px;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        main_layout.addWidget(self.btn_analyze, 0, Qt.AlignCenter)

        # Добавляем вертикальный отступ после кнопок
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Общий стиль окна (как в авторизации)
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
                font-family: Arial;
            }
        """)

        self.setLayout(main_layout)


class ModeSelectionPresenter:
    def __init__(self, view: ModeSelectionView):
        self.view = view
        self.current_user = view.current_user
        self.view.btn_create.clicked.connect(self.open_creation_mode)
        self.view.btn_analyze.clicked.connect(self.open_analysis_mode)

    def open_creation_mode(self):
        from EditingMode.EditingModeView import EditingModeView
        from EditingMode.EditingModePresenter import EditingModePresenter
        self.creation_window = EditingModeView(self.current_user)
        self.creation_presenter = EditingModePresenter(self.creation_window)
        self.creation_window.show()
        self.view.close()

    def open_analysis_mode(self):
        from AnalysisMode.AnalysisModeView import AnalysisModeView
        from AnalysisMode.AnalysisModePresenter import AnalysisModePresenter
        self.analysis_window = AnalysisModeView(self.current_user)
        self.analysis_presenter = AnalysisModePresenter(self.analysis_window)
        self.analysis_window.show()
        self.view.close()
