from EditingMode.EditingModeView import EditingModeView
from EditingMode.OsteoartritModel import OsteoartritModel
from Services.CloudService import GoogleDriveService
from PySide6.QtWidgets import (QListWidgetItem, QTableWidget, QTableWidgetItem, QDialogButtonBox,
                               QFileDialog, QMessageBox, QDialog, QFormLayout, QTextEdit,
                               QLineEdit, QComboBox, QInputDialog, QVBoxLayout, QLabel)
from PySide6.QtCore import Qt
import pandas as pd


class EditingModePresenter:
    def __init__(self, view: EditingModeView, model: OsteoartritModel):
        self.view = view
        self.model = model
        self.current_file = None
        self.current_record_index = -1  # -1 means new record
        self.current_page = 0
        self.connect_signals()

    def connect_signals(self):
        self.view.btn_load_local.clicked.connect(self.load_local_data)
        self.view.btn_save_local.clicked.connect(self.save_local_data)
        self.view.btn_load_from_cloud.clicked.connect(self.load_data_from_cloud)
        self.view.btn_save_to_cloud.clicked.connect(self.save_data_to_cloud)
        self.view.btn_save_as.clicked.connect(self.save_data_as)

        self.view.btn_add_row.clicked.connect(self.add_row)
        self.view.btn_edit_row.clicked.connect(self.edit_row)
        self.view.btn_delete_row.clicked.connect(self.delete_row)

        self.view.about_action.triggered.connect(self.show_about)
        self.view.analysis_action.triggered.connect(self.open_analysis_mode)

        self.view.next_button.clicked.connect(self.next_page)
        self.view.back_button.clicked.connect(self.prev_page)

        # Initialize view
        self.view.update_table(self.model.df)

    def add_row(self):
        self.current_record_index = -1
        self.current_page = 0
        self.view.clear_inputs()
        self.view.set_current_page_index(0)
        self.view.dialog.setWindowTitle("Добавить запись")
        self.view.dialog.show()
        self.center_dialog()

    def edit_row(self):
        row = self.view.get_selected_row_index()
        if row == -1:
            self.view.show_error("Выберите запись для редактирования")
            return

        self.current_record_index = row
        self.current_page = 0

        # Get data from model
        record = self.model.df.iloc[row]

        # Convert to input format
        values = {
            "age": record[1],
            "height": "",  # Not stored in model, will be recalculated
            "weight": "",  # Not stored in model, will be recalculated
            "dst": record[2],
            "gms": record[5],
            "skin_light": record[8],
            "skin_heavy": record[9],
            "keloid": record[10],
            "striae": record[11],
            "hemorrhages": record[12],
            "hernias": record[13],
            "ptosis": record[14],
            "tmj": record[15],
            "periodontosis": record[16],
            "dolicho": record[17],
            "kyphosis": record[20],
            "chest": record[21],
            "flatfeet": record[22],
            "valgus": record[23],
            "joint": record[24],
            "mvp": record[25],
            "varicose_light": record[26],
            "varicose_heavy": record[27],
            "myopia_light": record[28],
            "myopia_heavy": record[29],
            "gallbladder": record[30],
            "gerd": record[31],
            "hypotension": record[32]
        }

        # Calculate height and weight from BMI
        bmi = float(record[4])
        if bmi > 0:
            # Assume standard height to calculate weight
            height = 170  # cm
            weight = bmi * (height / 100) ** 2
            values["height"] = str(height)
            values["weight"] = str(round(weight, 1))

        self.view.set_input_values(values)
        self.view.set_current_page_index(0)
        self.view.dialog.setWindowTitle("Редактировать запись")
        self.view.dialog.show()
        self.center_dialog()

    def delete_row(self):
        row = self.view.get_selected_row_index()
        if row == -1:
            self.view.show_error("Выберите запись для удаления")
            return

        reply = QMessageBox.question(
            self.view, "Удаление",
            "Вы уверены, что хотите удалить выбранную запись?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.model.delete_record(row)
            self.view.update_table(self.model.df)

    def center_dialog(self):
        # Получаем геометрию главного окна
        main_window_rect = self.view.frameGeometry()
        # Получаем центр главного окна
        center_point = main_window_rect.center()
        # Получаем геометрию диалога
        dialog_rect = self.view.dialog.frameGeometry()
        # Устанавливаем центр диалога в центр главного окна
        dialog_rect.moveCenter(center_point)
        # Перемещаем диалог
        self.view.dialog.move(dialog_rect.topLeft())

    def next_page(self):
        if self.current_page == 22:  # Last page
            self.save_record()
            return

        # Validate current page
        if not self.validate_current_page():
            return

        self.current_page += 1
        self.view.set_current_page_index(self.current_page)
        self.center_dialog()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.view.set_current_page_index(self.current_page)
            self.center_dialog()

    def validate_current_page(self):
        values = self.view.get_input_values()

        if self.current_page == 0:  # Age, height, weight
            try:
                age = int(values["age"])
                height = float(values["height"])
                weight = float(values["weight"])
                if age <= 0 or height <= 0 or weight <= 0:
                    raise ValueError
            except ValueError:
                self.view.show_error(
                    "Введите корректные числовые значения (возраст - целое число, рост и вес - положительные числа)")
                return False

        elif self.current_page == 1:  # DST
            try:
                dst = int(values["dst"])
                if dst not in (0, 1):
                    raise ValueError
            except ValueError:
                self.view.show_error("ДСТ должно быть 0 или 1")
                return False

        elif self.current_page == 2:  # GMS
            try:
                gms = int(values["gms"])
                if not 1 <= gms <= 9:
                    raise ValueError
            except ValueError:
                self.view.show_error("ГМС должно быть целым числом от 1 до 9")
                return False

        # Other pages with 0/1 values
        elif 3 <= self.current_page <= 22:
            field_names = {
                3: ["skin_light", "skin_heavy"],
                4: ["keloid"],
                5: ["striae"],
                6: ["hemorrhages"],
                7: ["hernias"],
                8: ["ptosis"],
                9: ["tmj"],
                10: ["periodontosis"],
                11: ["dolicho"],
                12: ["kyphosis"],
                13: ["chest"],
                14: ["flatfeet"],
                15: ["valgus"],
                16: ["joint"],
                17: ["mvp"],
                18: ["varicose_light", "varicose_heavy"],
                19: ["myopia_light", "myopia_heavy"],
                20: ["gallbladder"],
                21: ["gerd"],
                22: ["hypotension"]
            }

            fields = field_names[self.current_page]
            for field in fields:
                try:
                    val = int(values[field])
                    if val not in (0, 1):
                        raise ValueError
                except ValueError:
                    self.view.show_error(f"Поле {field} должно быть 0 или 1")
                    return False

        return True

    def save_record(self):
        values = self.view.get_input_values()

        # Получаем ID врача из current_user
        doctor_id = self.view.current_user.get('ID', 0)


        # Calculate derived values
        try:
            age = int(values["age"])
            height = float(values["height"])
            weight = float(values["weight"])
            dst = int(values["dst"])
            gms = int(values["gms"])

            # Calculate BMI
            bmi = weight / ((height / 100) ** 2)
            bmi_under_25 = 1 if bmi < 25 else 0

            # Calculate GMS.2
            if gms < 4:
                gms2 = 1
            elif 4 <= gms <= 5:
                gms2 = 2
            else:
                gms2 = 3

            # Calculate GMS light and expressed
            gms_light = 1 if gms2 == 2 else 0
            gms_expressed = 1 if gms2 == 3 else 0

            # Sum of binary features (excluding disease, age, dst, sum, bmi, gms, gms2)
            binary_features = [
                int(values["skin_light"]),
                int(values["skin_heavy"]),
                int(values["keloid"]),
                int(values["striae"]),
                int(values["hemorrhages"]),
                int(values["hernias"]),
                int(values["ptosis"]),
                int(values["tmj"]),
                int(values["periodontosis"]),
                int(values["dolicho"]),
                gms_light,
                gms_expressed,
                int(values["kyphosis"]),
                int(values["chest"]),
                int(values["flatfeet"]),
                int(values["valgus"]),
                int(values["joint"]),
                int(values["mvp"]),
                int(values["varicose_light"]),
                int(values["varicose_heavy"]),
                int(values["myopia_light"]),
                int(values["myopia_heavy"]),
                int(values["gallbladder"]),
                int(values["gerd"]),
                int(values["hypotension"]),
                doctor_id
            ]

            feature_sum = sum(binary_features)
            disease = 1 if feature_sum >= 5 else 0

            # Create record
            record = [
                disease,  # Болезнь
                age,  # Возраст
                dst,  # ДСТ
                feature_sum,  # Сумма
                round(bmi, 2),  # ИМТ
                gms,  # ГМС
                gms2,  # ГМС.2
                bmi_under_25,  # ИМТ<25
                int(values["skin_light"]),  # кожа легк
                int(values["skin_heavy"]),  # кожа тяж
                int(values["keloid"]),  # Келлоид
                int(values["striae"]),  # Стрии
                int(values["hemorrhages"]),  # Геморрагии
                int(values["hernias"]),  # Грыжи
                int(values["ptosis"]),  # Птозы
                int(values["tmj"]),  # Хруст ВЧС
                int(values["periodontosis"]),  # Парадонтоз
                int(values["dolicho"]),  # Долихостен
                gms_light,  # ГМС легк
                gms_expressed,  # ГМС выраж
                int(values["kyphosis"]),  # Кифоз/лордоз
                int(values["chest"]),  # Деф гр клет
                int(values["flatfeet"]),  # Плоскост
                int(values["valgus"]),  # Вальг стопа
                int(values["joint"]),  # Хруст суст
                int(values["mvp"]),  # ПМК
                int(values["varicose_light"]),  # Варик лег
                int(values["varicose_heavy"]),  # Варик тяж
                int(values["myopia_light"]),  # Миопия лег
                int(values["myopia_heavy"]),  # Миопия тяж
                int(values["gallbladder"]),  # Жел пуз.
                int(values["gerd"]),  # ГЭРБ
                int(values["hypotension"]),  # Гипотенз
                doctor_id
            ]

            # Add or update record
            if self.current_record_index == -1:
                self.model.add_record(record)
            else:
                self.model.update_record(self.current_record_index, record)

            self.view.update_table(self.model.df)
            self.view.dialog.close()
            QMessageBox.information(self.view, "Успех!", "Данные успешно добавлены!")

        except ValueError as e:
            self.view.show_error(f"Ошибка в данных: {str(e)}")

    def update_columns_list(self):
        """Обновление списка столбцов"""
        self.view.columns_list.clear()
        if self.model.df is not None:
            for col in self.model.df.columns:
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
                self.model.df = pd.read_excel(file_path)
            elif file_path.lower().endswith('.csv'):
                # Чтение CSV файла с автоматическим определением разделителя
                self.model.df = pd.read_csv(file_path, sep=None, engine='python')
            else:
                pass

            self.view.file_path_edit.setText(file_path)
            self.current_file = file_path
            self.view.update_table(self.model.df)
            self.update_columns_list()
            QMessageBox.information(self.view, "Успех", "Файл успешно загружен")

        except Exception as e:
            QMessageBox.critical(self.view, "Ошибка", f"Не удалось загрузить файл:\n{str(e)}")

    def save_data_as(self):
        """Сохранение данных в файл"""
        if self.model.df.empty:
            QMessageBox.warning(self.view, "Ошибка", "Нет данных для сохранения!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self.view, "Сохранить данные", "",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.model.df.to_csv(file_path, index=False)
                else:
                    self.model.df.to_excel(file_path, index=False)
                QMessageBox.information(self.view, "Успех", "Данные успешно сохранены!")
            except Exception as e:
                QMessageBox.critical(self.view, "Ошибка", f"Ошибка сохранения:\n{str(e)}")

    def save_local_data(self):
        """Сохранение данных в Excel"""
        if self.model.df.empty:
            QMessageBox.warning(self.view, "Ошибка", "Нет данных для сохранения!")
            return

        if self.current_file:
            try:
                if self.current_file.endswith('.csv'):
                    self.model.df.to_csv(self.current_file, index=False)
                else:
                    self.model.df.to_excel(self.current_file, index=False)

                QMessageBox.information(self.view, "Успех", "Данные успешно сохранены!")
            except Exception as e:
                QMessageBox.critical(self.view, "Ошибка", f"Ошибка сохранения:\n{str(e)}")
        else:
            self.save_data_as()

    def load_data_from_cloud(self):
        """Загружает данные из Google Диска."""
        cloud_service = GoogleDriveService(parent_ui=self.view)
        self.model.df, file, error = cloud_service.load_from_cloud()

        if error:
            QMessageBox.critical(self.view, "Ошибка", error)
        else:
            # Обновление интерфейса
            self.view.update_table(self.model.df)
            self.update_columns_list()
            self.view.file_path_edit.setText(file['name'])
            QMessageBox.information(self.view, "Успех", "Файл успешно загружен")

    def save_data_to_cloud(self):
        """Сохраняет данные в Google Диск."""
        if self.model.df.empty:
            QMessageBox.warning(self.view, "Ошибка", "Нет данных для сохранения!")
            return

        cloud_service = GoogleDriveService(self.model.df, parent_ui=self.view)
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
