import os
import sys
from PySide6.QtWidgets import QApplication, QDialog
from Login.LoginView import LoginView
from Login.LoginModel import LoginModel
from Login.LoginPresenter import LoginPresenter
from ModeSelection import ModeSelectionView, ModeSelectionPresenter


def get_db_path():
    if getattr(sys, 'frozen', False):
        # Если запущено из exe, ищем рядом с exe
        base_path = os.path.dirname(sys.executable)
    else:
        # Если запущено из исходников, используем относительный путь
        base_path = os.path.dirname(__file__)

    return os.path.join(base_path, "databases", "doctors_db.xlsx")


db_users_file_name = get_db_path()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    login_view = LoginView()
    login_model = LoginModel(db_users_file_name)
    login_presenter = LoginPresenter(login_view, login_model)
    login_view.show()

    if login_view.exec() == QDialog.DialogCode.Accepted:
        mode_window = ModeSelectionView(login_presenter.current_user)
        mode_presenter = ModeSelectionPresenter(mode_window)
        mode_window.show()
        sys.exit(app.exec())
    else:
        # Просто завершаем программу, если авторизация не пройдена
        sys.exit()