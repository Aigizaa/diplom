from EditingMode.EditingModeView import EditingModeView
from Services.CloudService import GoogleDriveService
from PySide6.QtWidgets import (QListWidgetItem, QTableWidget, QTableWidgetItem, QDialogButtonBox,
                               QFileDialog, QMessageBox, QDialog, QFormLayout, QTextEdit,
                               QLineEdit, QComboBox, QInputDialog, QVBoxLayout, QLabel)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
import pandas as pd


class EditingModePresenter:
    def __init__(self, view: EditingModeView):
        self.view = view
        self.data = pd.DataFrame()
        self.current_file = None
        self.connect_signals()

    def connect_signals(self):
        self.view.btn_load_local.clicked.connect(self.load_local_data)
        self.view.btn_save_local.clicked.connect(self.save_local_data)
        self.view.btn_load_from_cloud.clicked.connect(self.load_data_from_cloud)
        self.view.btn_save_to_cloud.clicked.connect(self.save_data_to_cloud)
        self.view.btn_save_as.clicked.connect(self.save_data_as)

        self.view.btn_add_table.clicked.connect(self.create_table)
        #self.view.btn_edit_table.clicked.connect(self.edit_table)
        self.view.btn_delete_table.clicked.connect(self.delete_table)

        self.view.btn_add_row.clicked.connect(self.add_row)
        self.view.btn_edit_row.clicked.connect(self.edit_row)
        self.view.btn_delete_row.clicked.connect(self.delete_row)

        self.view.about_action.triggered.connect(self.show_about)
        self.view.analysis_action.triggered.connect(self.open_analysis_mode)

    def create_table(self):
        if not self.data.empty:
            msg = QMessageBox.warning(self.view, "Созданиие новой таблицы",
                                      "Создать новую таблицу? Предыдущая таблица будет удалена!",
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                return

        columns, ok = QInputDialog.getText(
            self.view, "Создание новой таблицы",
            "Введите названия колонок через запятую:"
        )
        if ok and columns:
            columns = [col.strip() for col in columns.split(',')]
            self.data = pd.DataFrame(columns=columns)
            self.update_table()

    def delete_table(self):
        if not self.data.columns.empty:
            msg = QMessageBox.warning(self.view, "Удаление таблицы", "Вы уверены, что хотите удалить таблицу?",
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            if msg == QMessageBox.StandardButton.Cancel:
                return
            self.data = pd.DataFrame()
            self.update_table()
        else:
            QMessageBox.information(self.view, "Ошибка", "Таблицы и так нет!")

    def update_table(self):
        """Обновление таблицы на основе данных"""
        self.view.table.setRowCount(len(self.data))
        self.view.table.setColumnCount(len(self.data.columns))
        self.view.table.setHorizontalHeaderLabels(self.data.columns)

        for row in range(len(self.data)):
            for col in range(len(self.data.columns)):
                item = QTableWidgetItem(str(self.data.iloc[row, col]))
                self.view.table.setItem(row, col, item)

    def add_row(self):
        # Поочередно запрашиваем значения для каждой колонки
        new_record = {}
        for column in self.data.columns:
            value, ok = QInputDialog.getText(
                self.view, "Создание записи",
                f"Введите значение для '{column}':"
            )
            if not ok:
                return
            new_record[column] = value

        # Добавляем новую запись
        self.data = pd.concat([self.data, pd.DataFrame([new_record])], ignore_index=True)
        self.update_table()

    def edit_row(self):
        """Редактирование существующей записи"""
        if self.data.empty:
            QMessageBox.warning(self.view, "Ошибка", "Нет данных для редактирования")
            return

        # Выбор записи (правильное использование getInt)
        row, ok = QInputDialog.getInt(
            self.view, "Выбор записи",
            f"Введите номер записи (1-{len(self.data)}):",
            1, 1, len(self.data), 1
        )
        # Параметры: parent, title, label, value, min, max, step
        if not ok:
            return

        # Остальной код без изменений
        column, ok = QInputDialog.getItem(
            self.view, "Выбор колонки",
            "Выберите колонку для редактирования:",
            list(self.data.columns), 0, False
        )
        if not ok:
            return

        current_value = str(self.data.at[row - 1, column])
        new_value, ok = QInputDialog.getText(
            self.view, "Редактирование",
            f"Текущее значение: {current_value}\nНовое значение:"
        )
        if ok and new_value != current_value:
            self.data.at[row - 1, column] = new_value
            self.update_table()

    def delete_row(self):
        """Удаление записи"""
        if self.data.empty:
            QMessageBox.warning(self.view, "Ошибка", "Нет данных для удаления")
            return

        # Выбор записи (правильное использование getInt)
        row, ok = QInputDialog.getInt(
            self.view, "Выбор записи",
            f"Введите номер записи для удаления (1-{len(self.data)}):",
            1, 1, len(self.data), 1
        )
        # Параметры: parent, title, label, value, min, max, step
        if not ok:
            return

        reply = QMessageBox.question(
            self.view, 'Подтверждение удаления',
            f"Вы уверены, что хотите удалить запись №{row}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.data = self.data.drop(row - 1).reset_index(drop=True)
            self.update_table()
            QMessageBox.information(self.view, "Успех", "Запись успешно удалена.")

    def update_columns_list(self):
        """Обновление списка столбцов"""
        self.view.columns_list.clear()
        if self.data is not None:
            for col in self.data.columns:
                item = QListWidgetItem(col)
                self.view.columns_list.addItem(item)

    def load_local_data(self):
        """Загрузка Excel файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.view, "Открыть файл данных",
            "", "Excel Files (*.xlsx *.xls);;CSV Files (*.csv)"
        )
        if not file_path:
            return  # Пользователь отменил выбор файла

        try:
            if file_path.lower().endswith(('.xlsx', '.xls')):
                # Чтение Excel файла
                self.data = pd.read_excel(file_path)
            elif file_path.lower().endswith('.csv'):
                # Чтение CSV файла с автоматическим определением разделителя
                self.data = pd.read_csv(file_path, sep=None, engine='python')
            else:
                pass

            self.view.file_path_edit.setText(file_path)
            self.current_file = file_path
            self.update_table()
            self.update_columns_list()
            QMessageBox.information(self.view, "Успех", "Файл успешно загружен")

        except Exception as e:
            QMessageBox.critical(self.view, "Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def save_data_as(self):
        """Сохранение данных в файл"""
        if self.data is None:
            QMessageBox.warning(self.view, "Ошибка", "Нет данных для сохранения!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self.view, "Сохранить данные", "",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.data.to_csv(file_path, index=False)
                else:
                    self.data.to_excel(file_path, index=False)
                QMessageBox.information(self.view, "Успех", "Данные успешно сохранены!")
            except Exception as e:
                QMessageBox.critical(self.view, "Ошибка", f"Ошибка сохранения:\n{str(e)}")

    def save_local_data(self):
        """Сохранение данных в Excel"""
        if self.data is None:
            QMessageBox.warning(self.view, "Ошибка", "Нет данных для сохранения!")
            return

        if self.current_file:
            try:
                if self.current_file.endswith('.csv'):
                    self.data.to_csv(self.current_file, index=False)
                else:
                    self.data.to_excel(self.current_file, index=False)

                QMessageBox.information(self.view, "Успех", "Данные успешно сохранены!")
            except Exception as e:
                QMessageBox.critical(self.view, "Ошибка", f"Ошибка сохранения:\n{str(e)}")

    def load_data_from_cloud(self):
        """Загружает данные из Google Диска."""
        cloud_service = GoogleDriveService(parent_ui=self.view)
        self.data, file, error = cloud_service.load_from_cloud()

        if error:
            QMessageBox.critical(self.view, "Ошибка", error)
        else:
            # Обновление интерфейса
            self.update_table()
            self.update_columns_list()
            self.view.file_path_edit.setText(file['name'])
            QMessageBox.information(self.view, "Успех", "Файл успешно загружен")

    def save_data_to_cloud(self):
        """Сохраняет данные в Google Диск."""
        if self.data is None:
            QMessageBox.warning(self.view, "Ошибка", "Нет данных для сохранения!")
            return

        cloud_service = GoogleDriveService(self.data, parent_ui=self.view)
        result = cloud_service.save_to_cloud(self.view.current_user['ФИО'])
        if result.startswith("Ошибка"):
            QMessageBox.critical(self.view, "Ошибка", result)
        else:
            QMessageBox.information(self.view, "Успех", result)

    def open_analysis_mode(self):
        from AnalysisMode.AnalysisModeView import AnalysisModeView
        from AnalysisMode.AnalysisModePresenter import AnalysisModePresenter
        self.analysis_window = AnalysisModeView(self.view.current_user)
        self.analysis_presenter = AnalysisModePresenter(self.analysis_window)
        self.analysis_window.show()
        self.view.close()

    def show_about(self):
        """Информация о программе"""
        QMessageBox.about(self.view, "О программе",
                          "Анализатор биомедицинских данных v1.0\n"
                          "Для работы с клиническими показателями пациентов")