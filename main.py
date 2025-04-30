import sys
from PySide6.QtWidgets import QApplication, QDialog
from LoginWindow import LoginWindow
from ModeSelectionWindow import ModeSelectionWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()

    if login.exec() == QDialog.Accepted:
        # После успешной авторизации показываем окно выбора режима
        mode_window = ModeSelectionWindow(login.current_user)
        mode_window.show()
    else:
        # Если авторизация не пройдена - все равно разрешаем доступ
        # с тестовым пользователем (можно убрать в продакшене)
        test_user = {
            'ФИО': 'Тестовый пользователь',
            'Логин': 'debug_user',
            'access_level': 'full'
        }
        mode_window = ModeSelectionWindow(test_user)
        mode_window.show()

    sys.exit(app.exec())