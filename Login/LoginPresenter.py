from Login.LoginView import LoginView
from Login.LoginModel import LoginModel
from PySide6.QtWidgets import QMessageBox


class LoginPresenter:
    def __init__(self, view: LoginView, model: LoginModel):
        self.current_user = None
        self.view = view
        self.model = model
        self.view.btn_login.clicked.connect(self.verify_login_and_password)

    def verify_login_and_password(self):
        """Проверка логина и пароля"""
        login, password = self.view.get_login_and_password()

        if not login or not password:
            QMessageBox.warning(self.view, "Ошибка", "Введите логин и пароль!")
            return
        try:
            # Ищем пользователя в базе
            user = self.model.users_db[
                (self.model.users_db['Логин'] == login) &
                (self.model.users_db['Пароль'] == password)
                ]

            if not user.empty:
                # Сохраняем информацию о пользователе, включая ID
                self.current_user = {
                    'ID': user.iloc[0]['ID'],
                    'ФИО': user.iloc[0]['ФИО'],
                    'Логин': login
                }
                self.view.accept()
            else:
                QMessageBox.warning(self.view, "Ошибка", "Неверный логин или пароль!")
                self.view.password_edit.clear()

        except Exception as e:
            QMessageBox.critical(self.view, "Ошибка",
                                 f"Ошибка проверки учетных данных:\n{str(e)}")
