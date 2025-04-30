from PySide6.QtWidgets import (
    QWidget, QMainWindow, QFrame, QSplitter, QHBoxLayout)
from PySide6.QtCore import Qt


# Главное окно приложения
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Анализ биомедицинских данных")
        self.setWindowState(Qt.WindowMaximized)
        self.init_ui()

    def init_ui(self):
        pass
