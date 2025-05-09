import pandas as pd
import os


class LoginModel:
    def __init__(self, excel_path: str):
        self.users_db = None
        self.load_users_db(excel_path)

    def load_users_db(self, excel_path: str):
        """Загрузка базы пользователей из Excel файла"""
        try:
            db_path = os.path.abspath(excel_path)

            if not os.path.exists(db_path):
                # Создаем файл с тестовым пользователем и ID
                default_users = pd.DataFrame({
                    'ID': [1],
                    'ФИО': ['Иванов Иван Иванович'],
                    'Логин': ['admin'],
                    'Пароль': ['admin123']
                })
                default_users.to_excel(db_path, index=False)
                self.users_db = default_users
            else:
                # Читаем существующий файл
                self.users_db = pd.read_excel(db_path)
                # Если нет столбца ID, создаем его
                if 'ID' not in self.users_db.columns:
                    self.users_db['ID'] = range(1, len(self.users_db) + 1)
                    self.users_db.to_excel(db_path, index=False)

        except Exception as e:
            pass
            #QMessageBox.critical(self, "Ошибка",
            #                    f"Не удалось загрузить базу врачей:\n{str(e)}")
            #self.users_db = pd.DataFrame(columns=['ФИО', 'Логин', 'Пароль'])

