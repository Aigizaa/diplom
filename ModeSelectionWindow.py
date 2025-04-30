from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel,
                               QPushButton, QHBoxLayout)
from PySide6.QtCore import Qt


class ModeSelectionWindow(QWidget):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Выбор режима работы")
        self.setFixedSize(400, 200)

        layout = QVBoxLayout()

        # Надпись по центру
        label = QLabel("Выберите режим работы")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)

        # Горизонтальный layout для кнопок
        buttons_layout = QHBoxLayout()

        # Кнопка "Создание"
        btn_create = QPushButton("Создание")
        btn_create.setStyleSheet("font-size: 16px; padding: 10px;")
        btn_create.clicked.connect(self.open_create_mode)
        buttons_layout.addWidget(btn_create)

        # Кнопка "Анализ"
        btn_analyze = QPushButton("Анализ")
        btn_analyze.setStyleSheet("font-size: 16px; padding: 10px;")
        btn_analyze.clicked.connect(self.open_analyze_mode)
        buttons_layout.addWidget(btn_analyze)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def open_create_mode(self):
        from CreateBaseWindow import CreateBaseWindow
        self.create_window = CreateBaseWindow(self.current_user)
        self.create_window.show()
        self.close()

    def open_analyze_mode(self):
        from MainWindow import MainWindow
        self.analyze_window = MainWindow(self.current_user)
        self.analyze_window.show()
        self.close()