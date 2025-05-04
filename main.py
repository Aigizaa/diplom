import os
import sys
from PySide6.QtWidgets import QApplication, QDialog
from Login.LoginView import LoginView
from Login.LoginModel import LoginModel
from Login.LoginPresenter import LoginPresenter
from ModeSelection import ModeSelectionView, ModeSelectionPresenter


db_users_file_name = "databases/doctors_db.xlsx"

if __name__ == '__main__':
    app = QApplication(sys.argv)

    login_view = LoginView()
    login_model = LoginModel(db_users_file_name)
    login_presenter = LoginPresenter(login_view, login_model)
    login_view.show()

    if login_view.exec() == QDialog.DialogCode.Accepted:
        mode_window = ModeSelectionView(login_presenter.current_user)
        mode_presenter = ModeSelectionPresenter(mode_window, login_presenter.current_user)
        mode_window.show()
    else:
        # Если авторизация не пройдена - все равно разрешаем доступ
        # с тестовым пользователем (можно убрать в продакшене)
        test_user = {
            'ФИО': 'Тестовый пользователь',
            'Логин': 'debug_user',
            'access_level': 'full'
        }
        mode_window = ModeSelectionView(test_user)
        mode_presenter = ModeSelectionPresenter(mode_window, test_user)
        mode_window.show()

    sys.exit(app.exec())


