import sys
import pandas as pd
import os

from PySide6.QtWidgets import QMessageBox


def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсу """
    if getattr(sys, 'frozen', False):
        # Для exe - ищем рядом с исполняемым файлом
        base_path = os.path.dirname(sys.executable)
    else:
        # Для разработки - используем обычный путь
        base_path = os.path.dirname(__file__)

    return os.path.join(base_path, relative_path)

class LoginModel:
    def __init__(self, excel_path: str):
        self.users_db = None
        self.excel_path = excel_path
        self.load_users_db()

    def load_users_db(self):
        """Загрузка базы пользователей из Excel файла с обработкой ошибок"""
        try:
            db_path = resource_path(self.excel_path)

            # Проверяем существование папки databases
            db_dir = os.path.dirname(db_path)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
                QMessageBox.information(
                    None,
                    "Информация",
                    f"Создана папка для базы данных: {db_dir}"
                )

            # Если файл не существует, создаем новый с тестовым пользователем
            if not os.path.exists(db_path):
                default_users = pd.DataFrame({
                    'ID': [1],
                    'ФИО': ['Иванов Иван Иванович'],
                    'Логин': ['admin'],
                    'Пароль': ['admin123']
                })

                try:
                    default_users.to_excel(db_path, index=False)
                    self.users_db = default_users
                    QMessageBox.information(
                        None,
                        "Создана новая база данных",
                        f"Создан новый файл базы данных по пути: {db_path}\n"
                        "Добавлен тестовый пользователь:\n"
                        "Логин: admin\nПароль: admin123"
                    )
                except Exception as create_error:
                    raise Exception(f"Не удалось создать файл базы данных: {str(create_error)}")

            # Чтение существующего файла
            try:
                self.users_db = pd.read_excel(db_path)

                # Проверка обязательных столбцов
                required_columns = ['ID', 'ФИО', 'Логин', 'Пароль']
                for col in required_columns:
                    if col not in self.users_db.columns:
                        raise Exception(f"Отсутствует обязательный столбец: {col}")

                # Если нет столбца ID, создаем его
                if 'ID' not in self.users_db.columns:
                    self.users_db['ID'] = range(1, len(self.users_db) + 1)
                    self.users_db.to_excel(db_path, index=False)

            except Exception as read_error:
                raise Exception(f"Ошибка чтения файла базы данных: {str(read_error)}")

        except Exception as e:
            # Создаем пустой DataFrame в памяти, если не удалось загрузить/создать файл
            self.users_db = pd.DataFrame(columns=['ID', 'ФИО', 'Логин', 'Пароль'])
            QMessageBox.critical(
                None,
                "Ошибка базы данных",
                f"Не удалось загрузить базу пользователей:\n{str(e)}\n"
                "Работа ведется с временной базой в памяти. Изменения не будут сохранены."
            )

            # Добавляем тестового пользователя в память
            self.users_db.loc[0] = {
                'ID': 1,
                'ФИО': 'Тестовый пользователь',
                'Логин': 'test',
                'Пароль': 'test123'
            }