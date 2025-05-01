from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                               QFileDialog, QMessageBox, QDialog, QFormLayout,
                               QLineEdit, QComboBox, QInputDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
import pandas as pd
import os


class CreateBaseWindow(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.data = pd.DataFrame()
        self.current_file = None
        self.init_ui()
        self.create_menus()
        self.setup_connections()

    def init_ui(self):
        self.setWindowTitle(f"Режим создания - {self.current_user['ФИО']}")
        self.setFixedSize(1100, 700)

        from MainWindow import resource_path
        icon_path = resource_path("resources/icon.png")
        self.setWindowIcon(QIcon(icon_path))

        # Главный контейнер
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Боковая панель с кнопками
        button_panel = QWidget()
        button_layout = QVBoxLayout(button_panel)
        button_layout.setAlignment(Qt.AlignTop)

        buttons = [
            ("Загрузить файл", self.load_file),
            ("Сохранить", self.save_file),
            ("Создать запись", self.create_record),
            ("Редактировать", self.edit_record),
            ("Удалить", self.delete_record)
        ]

        for text, callback in buttons:
            btn = QPushButton(text)
            btn.setFixedSize(150, 40)
            btn.setStyleSheet("font-size: 14px;")
            btn.clicked.connect(callback)
            button_layout.addWidget(btn)

        button_layout.addStretch()
        main_layout.addWidget(button_panel)

        # Центральная область с таблицей
        self.table = QTableWidget()
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        main_layout.addWidget(self.table, stretch=1)

        self.setCentralWidget(main_widget)

    def create_menus(self):
        menubar = self.menuBar()
        # Меню "Справка"
        help_menu = menubar.addMenu("Справка")

        # Пункт "Памятка по признакам"
        #legend_action = QAction("Памятка по признакам", self)
        #legend_action.triggered.connect(self.show_legend)
        #help_menu.addAction(legend_action)

        # Пункт "О программе"
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # меню "Режим"
        mode_menu = menubar.addMenu("Режим")

        # Пункт Анализ
        analyze_action = QAction("Анализ", self)
        analyze_action.setCheckable(True)
        analyze_action.setChecked(False)
        analyze_action.triggered.connect(self.open_analyze_mode)
        mode_menu.addAction(analyze_action)

        # Пункт Создание
        from ModeSelectionWindow import ModeSelectionWindow
        create_action = QAction("Создание и пополнение", self)
        create_action.setCheckable(True)
        create_action.setChecked(True)
        mode_menu.addAction(create_action)

    def show_about(self):
        """Информация о программе"""
        QMessageBox.about(self, "О программе",
                          "Анализатор биомедицинских данных v1.0\n"
                          "Для работы с клиническими показателями пациентов")

    def open_analyze_mode(self):
        from MainWindow import MainWindow
        self.analyze_window = MainWindow(self.current_user)
        self.analyze_window.show()
        self.close()

    def setup_connections(self):
        """Настройка обработчиков событий"""
        pass

    def load_file(self):
        """Загрузка Excel файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл", "", "Excel Files (*.xlsx *.xls)"
        )
        if file_path:
            try:
                self.data = pd.read_excel(file_path)
                self.current_file = file_path
                self.update_table()
                QMessageBox.information(self, "Успех", "Файл успешно загружен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def save_file(self):
        """Сохранение данных в Excel"""
        if self.data.empty:
            QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения")
            return

        if self.current_file:
            try:
                self.data.to_excel(self.current_file, index=False)
                QMessageBox.information(self, "Успех", "Файл успешно сохранен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
        else:
            self.save_file_as()

    def save_file_as(self):
        """Сохранение с выбором имени файла"""
        if self.data.empty:
            QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл", "", "Excel Files (*.xlsx)"
        )
        if file_path:
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            self.current_file = file_path
            self.save_file()

    def update_table(self):
        """Обновление таблицы на основе данных"""
        self.table.setRowCount(len(self.data))
        self.table.setColumnCount(len(self.data.columns))
        self.table.setHorizontalHeaderLabels(self.data.columns)

        for row in range(len(self.data)):
            for col in range(len(self.data.columns)):
                item = QTableWidgetItem(str(self.data.iloc[row, col]))
                self.table.setItem(row, col, item)

    def create_record(self):
        """Создание новой записи"""
        if self.data.empty:
            # Если таблица пуста, создаем колонки
            columns, ok = QInputDialog.getText(
                self, "Создание таблицы",
                "Введите названия колонок через запятую:"
            )
            if ok and columns:
                columns = [col.strip() for col in columns.split(',')]
                self.data = pd.DataFrame(columns=columns)
                self.update_table()
            else:
                return

        # Поочередно запрашиваем значения для каждой колонки
        new_record = {}
        for column in self.data.columns:
            value, ok = QInputDialog.getText(
                self, "Создание записи",
                f"Введите значение для '{column}':"
            )
            if not ok:
                return
            new_record[column] = value

        # Добавляем новую запись
        self.data = pd.concat([self.data, pd.DataFrame([new_record])], ignore_index=True)
        self.update_table()

    def edit_record(self):
        """Редактирование существующей записи"""
        if self.data.empty:
            QMessageBox.warning(self, "Ошибка", "Нет данных для редактирования")
            return

        # Выбор записи (правильное использование getInt)
        row, ok = QInputDialog.getInt(
            self, "Выбор записи",
            f"Введите номер записи (1-{len(self.data)}):",
            1, 1, len(self.data), 1
        )
        # Параметры: parent, title, label, value, min, max, step
        if not ok:
            return

        # Остальной код без изменений
        column, ok = QInputDialog.getItem(
            self, "Выбор колонки",
            "Выберите колонку для редактирования:",
            list(self.data.columns), 0, False
        )
        if not ok:
            return

        current_value = str(self.data.at[row - 1, column])
        new_value, ok = QInputDialog.getText(
            self, "Редактирование",
            f"Текущее значение: {current_value}\nНовое значение:"
        )
        if ok and new_value != current_value:
            self.data.at[row - 1, column] = new_value
            self.update_table()

    def delete_record(self):
        """Удаление записи"""
        if self.data.empty:
            QMessageBox.warning(self, "Ошибка", "Нет данных для удаления")
            return

        # Выбор записи (правильное использование getInt)
        row, ok = QInputDialog.getInt(
            self, "Выбор записи",
            f"Введите номер записи для удаления (1-{len(self.data)}):",
            1, 1, len(self.data), 1
        )
        # Параметры: parent, title, label, value, min, max, step
        if not ok:
            return

        # Остальной код без изменений
        record_data = "\n".join(
            f"{col}: {self.data.iloc[row - 1][col]}"
            for col in self.data.columns
        )

        reply = QMessageBox.question(
            self, 'Подтверждение удаления',
            f"Вы уверены, что хотите удалить запись?\n\n{record_data}",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.data = self.data.drop(row - 1).reset_index(drop=True)
            self.update_table()