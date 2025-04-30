import sys
from PySide6.QtWidgets import QApplication, QDialog
from LoginWindow import LoginWindow
from MainWindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Создаем и показываем окно авторизации
    login = LoginWindow()
    if login.exec() == QDialog.Accepted:
        # Если авторизация успешна, показываем главное окно
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        # Если авторизация не пройдена, закрываем приложение
        sys.exit()