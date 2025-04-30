from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget


class CreateBaseWindow(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Режим создания - {self.current_user['ФИО']}")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Это окно для создания базы данных")
        label.setStyleSheet("font-size: 16px;")
        layout.addWidget(label)

        # Здесь можно добавить элементы интерфейса для создания базы

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)