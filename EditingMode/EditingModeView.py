from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                               QStackedWidget, QMessageBox, QDialog, QFormLayout,
                               QLineEdit, QComboBox, QInputDialog, QSplitter, QListWidget, QGroupBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QPixmap
import pandas as pd
import os


class EditingModeView(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user

        # Элементы на левой панели
        self.file_path_edit = QLineEdit()
        self.btn_load_local = QPushButton("Загрузить данные")
        self.btn_save_local = QPushButton("Сохранить данные")
        self.btn_save_as = QPushButton("Сохранить как...")
        self.btn_load_from_cloud = QPushButton("Загрузить из облака")
        self.btn_save_to_cloud = QPushButton("Сохранить в облако")

        self.btn_add_row = QPushButton("Добавить запись")
        self.btn_edit_row = QPushButton("Изменить запись")
        self.btn_delete_row = QPushButton("Удалить запись")

        self.columns_list = QListWidget()

        # Центральная область с таблицей
        self.table = QTableWidget()
        self.init_ui()

        # Меню
        self.analysis_action = QAction("Анализ", self)
        self.about_action = QAction("О программе", self)
        self.create_menus()

    def init_ui(self):
        self.setWindowTitle(f"Режим создания - {self.current_user['ФИО']}")
        self.setWindowState(Qt.WindowState.WindowMaximized)
        icon_path = os.path.abspath("resources/icon.png")
        self.setWindowIcon(QIcon(icon_path))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель управления
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Группа "Файл"
        group_file = QGroupBox("Файл")
        layout_file = QVBoxLayout(group_file)
        layout_file.addWidget(QLabel("Путь к файлу:"))
        layout_file.addWidget(self.file_path_edit)
        layout_file.addWidget(self.btn_load_local)
        layout_file.addWidget(self.btn_save_local)
        layout_file.addWidget(self.btn_save_as)
        layout_file.addWidget(self.btn_load_from_cloud)
        layout_file.addWidget(self.btn_save_to_cloud)
        left_layout.addWidget(group_file)

        # Группа "Запись"
        group_actions = QGroupBox("Запись")
        layout_actions = QVBoxLayout(group_actions)
        layout_actions.addWidget(self.btn_add_row)
        layout_actions.addWidget(self.btn_edit_row)
        layout_actions.addWidget(self.btn_delete_row)
        left_layout.addWidget(group_actions)

        # Группа столбцы
        group_columns = QGroupBox("Столбцы")
        layout_columns = QVBoxLayout(group_columns)
        layout_columns.addWidget(self.columns_list)
        left_layout.addWidget(group_columns)

        # Правая панель с таблицей
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # центральная таблица
        self.table.setColumnCount(32)
        self.table.setHorizontalHeaderLabels([
            "Болезнь", "Возраст", "ДСТ", "Сумма", "ИМТ", "ГМС", "ГМС.2",
            "ИМТ<25", "кожа легк", "кожа тяж", "Келлоид", "Стрии", "Геморрагии",
            "Грыжи", "Птозы", "Хруст ВЧС", "Парадонтоз", "Долихостен",
            "ГМС легк", "ГМС выраж", "Кифоз/лордоз", "Деф гр клет", "Плоскост",
            "Вальг стопа", "Хруст суст", "ПМК", "Варик лег", "Варик тяж",
            "Миопия лег", "Миопия тяж", "Жел пуз.", "ГЭРБ", "Гипотенз"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        right_layout.addWidget(self.table)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)  # индекс 0 — первый виджет
        splitter.setStretchFactor(1, 4)  # индекс 1 — второй виджет

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # Dialog for adding/editing records
        self.dialog = QWidget()
        self.dialog.setWindowTitle("Добавить запись")
        self.dialog_layout = QVBoxLayout(self.dialog)

        self.stacked_widget = QStackedWidget()
        self.dialog_layout.addWidget(self.stacked_widget)

        self.navigation_layout = QHBoxLayout()
        self.back_button = QPushButton("Назад")
        self.next_button = QPushButton("Далее")
        self.navigation_layout.addWidget(self.back_button)
        self.navigation_layout.addWidget(self.next_button)
        self.dialog_layout.addLayout(self.navigation_layout)

        # Create pages for the dialog
        self.create_pages()

    def create_menus(self):
        menubar = self.menuBar()
        # Меню "Справка"
        help_menu = menubar.addMenu("Справка")

        # Пункт "О программе"
        help_menu.addAction(self.about_action)

        # меню "Режим"
        mode_menu = menubar.addMenu("Режим")

        # Пункт Анализ
        self.analysis_action.setCheckable(True)
        self.analysis_action.setChecked(False)
        mode_menu.addAction(self.analysis_action)

        # Пункт Создание
        create_action = QAction("Создание и пополнение", self)
        create_action.setCheckable(True)
        create_action.setChecked(True)
        mode_menu.addAction(create_action)

    def create_pages(self):
        # Страница 1: Возраст, рост, вес
        page1 = QWidget()
        layout1 = QVBoxLayout(page1)

        self.dialog.setFixedSize(300, 200)

        # Поле для возраста
        age_layout = QVBoxLayout()
        age_layout.setSpacing(5)
        age_layout.addWidget(QLabel("Возраст:"))
        self.age_edit = QLineEdit()
        self.age_edit.setMaximumWidth(200)  # Ограничиваем ширину
        age_layout.addWidget(self.age_edit)
        layout1.addLayout(age_layout)

        # Поле для роста
        height_layout = QVBoxLayout()
        height_layout.setSpacing(5)
        height_layout.addWidget(QLabel("Рост (см):"))
        self.height_edit = QLineEdit()
        self.height_edit.setMaximumWidth(200)
        height_layout.addWidget(self.height_edit)
        layout1.addLayout(height_layout)

        # Поле для веса
        weight_layout = QVBoxLayout()
        weight_layout.setSpacing(5)
        weight_layout.addWidget(QLabel("Вес (кг):"))
        self.weight_edit = QLineEdit()
        self.weight_edit.setMaximumWidth(200)
        weight_layout.addWidget(self.weight_edit)
        layout1.addLayout(weight_layout)
        layout1.addStretch()  # Добавляем растяжимое пространство внизу
        self.stacked_widget.addWidget(page1)

        # Страница 2: ДСТ
        page2 = QWidget()
        layout2 = QVBoxLayout(page2)
        layout2.setContentsMargins(20, 20, 20, 20)
        layout2.setSpacing(15)

        dst_layout = QVBoxLayout()
        dst_layout.setSpacing(5)
        dst_layout.addWidget(QLabel("Дисплазия соединительной ткани (0 или 1):"))
        self.dst_edit = QLineEdit()
        self.dst_edit.setMaximumWidth(200)
        dst_layout.addWidget(self.dst_edit)
        layout2.addLayout(dst_layout)
        layout2.addStretch()
        self.stacked_widget.addWidget(page2)

        # Page 3: GMS
        page3 = QWidget()
        layout3 = QVBoxLayout(page3)
        self.gms_image = QLabel()
        self.gms_image.setPixmap(QPixmap("Pictures/ГМС.png").scaled(900, 700, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout3.addWidget(self.gms_image)
        layout3.addWidget(QLabel("Гипермобильность суставов (1-9):"))
        self.gms_edit = QLineEdit()
        layout3.addWidget(self.gms_edit)
        self.stacked_widget.addWidget(page3)

        # Page 4: Skin
        page4 = QWidget()
        layout4 = QVBoxLayout(page4)
        self.skin_image = QLabel()
        self.skin_image.setPixmap(QPixmap("Pictures/Кожа.png").scaled(900, 700, Qt.AspectRatioMode.KeepAspectRatio,
                                                                      Qt.TransformationMode.SmoothTransformation))
        layout4.addWidget(self.skin_image)
        layout4.addWidget(QLabel("Гиперрастяжимость кожи легкой степени (0 или 1):"))
        self.skin_light_edit = QLineEdit()
        layout4.addWidget(self.skin_light_edit)
        layout4.addWidget(QLabel("Гиперрастяжимость кожи тяжелой степени (0 или 1):"))
        self.skin_heavy_edit = QLineEdit()
        layout4.addWidget(self.skin_heavy_edit)
        self.stacked_widget.addWidget(page4)

        # Page 5: Keloid
        page5 = QWidget()
        layout5 = QVBoxLayout(page5)
        self.keloid_image = QLabel()
        self.keloid_image.setPixmap(QPixmap("Pictures/Келоидные рубцы.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                            Qt.TransformationMode.SmoothTransformation))
        layout5.addWidget(self.keloid_image)
        layout5.addWidget(QLabel("Келоидные рубцы (0 или 1):"))
        self.keloid_edit = QLineEdit()
        layout5.addWidget(self.keloid_edit)
        self.stacked_widget.addWidget(page5)

        # Page 6: Stretch marks
        page6 = QWidget()
        layout6 = QVBoxLayout(page6)
        self.striae_image = QLabel()
        self.striae_image.setPixmap(QPixmap("Pictures/Стрии.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout6.addWidget(self.striae_image)
        layout6.addWidget(QLabel("Стрии (0 или 1):"))
        self.striae_edit = QLineEdit()
        layout6.addWidget(self.striae_edit)
        self.stacked_widget.addWidget(page6)

        # Page 7: Hemorrhages
        page7 = QWidget()
        layout7 = QVBoxLayout(page7)
        self.hemorrhages_image = QLabel()
        self.hemorrhages_image.setPixmap(QPixmap("Pictures/Геморрагии.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout7.addWidget(self.hemorrhages_image)
        layout7.addWidget(QLabel("Геморрагии (0 или 1):"))
        self.hemorrhages_edit = QLineEdit()
        layout7.addWidget(self.hemorrhages_edit)
        self.stacked_widget.addWidget(page7)

        # Page 8: Hernias
        page8 = QWidget()
        layout8 = QVBoxLayout(page8)
        self.hernias_image = QLabel()
        self.hernias_image.setPixmap(QPixmap("Pictures/Грыжи.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout8.addWidget(self.hernias_image)
        layout8.addWidget(QLabel("Грыжи (0 или 1):"))
        self.hernias_edit = QLineEdit()
        layout8.addWidget(self.hernias_edit)
        self.stacked_widget.addWidget(page8)

        # Page 9: Ptosis
        page9 = QWidget()
        layout9 = QVBoxLayout(page9)
        self.ptosis_image = QLabel()
        self.ptosis_image.setPixmap(QPixmap("Pictures/Птозы.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout9.addWidget(self.ptosis_image)
        layout9.addWidget(QLabel("Птозы (0 или 1):"))
        self.ptosis_edit = QLineEdit()
        layout9.addWidget(self.ptosis_edit)
        self.stacked_widget.addWidget(page9)

        # Page 10: TMJ click
        page10 = QWidget()
        layout10 = QVBoxLayout(page10)
        self.tmj_image = QLabel()
        self.tmj_image.setPixmap(QPixmap("Pictures/Хруст ВЧС.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout10.addWidget(self.tmj_image)
        layout10.addWidget(QLabel("Хруст ВЧС (0 или 1):"))
        self.tmj_edit = QLineEdit()
        layout10.addWidget(self.tmj_edit)
        self.stacked_widget.addWidget(page10)

        # Page 11: Periodontosis
        page11 = QWidget()
        layout11 = QVBoxLayout(page11)
        self.periodontosis_image = QLabel()
        self.periodontosis_image.setPixmap(QPixmap("Pictures/Парадонтоз.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout11.addWidget(self.periodontosis_image)
        layout11.addWidget(QLabel("Парадонтоз (0 или 1):"))
        self.periodontosis_edit = QLineEdit()
        layout11.addWidget(self.periodontosis_edit)
        self.stacked_widget.addWidget(page11)

        # Page 12: Dolichostenomelia
        page12 = QWidget()
        layout12 = QVBoxLayout(page12)
        self.dolicho_image = QLabel()
        self.dolicho_image.setPixmap(QPixmap("Pictures/Долихостеномелия.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout12.addWidget(self.dolicho_image)
        layout12.addWidget(QLabel("Долихостеномелия (0 или 1):"))
        self.dolicho_edit = QLineEdit()
        layout12.addWidget(self.dolicho_edit)
        self.stacked_widget.addWidget(page12)

        # Page 13: Kyphosis/Lordosis
        page13 = QWidget()
        layout13 = QVBoxLayout(page13)
        self.kyphosis_image = QLabel()
        self.kyphosis_image.setPixmap(QPixmap("Pictures/Кифоз_лордоз.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout13.addWidget(self.kyphosis_image)
        layout13.addWidget(QLabel("Гиперкифоз/гиперлордоз (0 или 1):"))
        self.kyphosis_edit = QLineEdit()
        layout13.addWidget(self.kyphosis_edit)
        self.stacked_widget.addWidget(page13)

        # Page 14: Chest deformity
        page14 = QWidget()
        layout14 = QVBoxLayout(page14)
        self.chest_image = QLabel()
        self.chest_image.setPixmap(QPixmap("Pictures/Деф гр клет.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout14.addWidget(self.chest_image)
        layout14.addWidget(QLabel("Деформация грудной клетки (0 или 1):"))
        self.chest_edit = QLineEdit()
        layout14.addWidget(self.chest_edit)
        self.stacked_widget.addWidget(page14)

        # Page 15: Flat feet
        page15 = QWidget()
        layout15 = QVBoxLayout(page15)
        self.flatfeet_image = QLabel()
        self.flatfeet_image.setPixmap(QPixmap("Pictures/Плоскостопие.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout15.addWidget(self.flatfeet_image)
        layout15.addWidget(QLabel("Плоскостопие (0 или 1):"))
        self.flatfeet_edit = QLineEdit()
        layout15.addWidget(self.flatfeet_edit)
        self.stacked_widget.addWidget(page15)

        # Page 16: Valgus foot
        page16 = QWidget()
        layout16 = QVBoxLayout(page16)
        self.valgus_image = QLabel()
        self.valgus_image.setPixmap(QPixmap("Pictures/Вальгус.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout16.addWidget(self.valgus_image)
        layout16.addWidget(QLabel("Вальгус стоп (0 или 1):"))
        self.valgus_edit = QLineEdit()
        layout16.addWidget(self.valgus_edit)
        self.stacked_widget.addWidget(page16)

        # Page 17: Joint click
        page17 = QWidget()
        layout17 = QVBoxLayout(page17)
        self.joint_image = QLabel()
        self.joint_image.setPixmap(QPixmap("Pictures/Хруст_в_суставах.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout17.addWidget(self.joint_image)
        layout17.addWidget(QLabel("Хруст суставов (0 или 1):"))
        self.joint_edit = QLineEdit()
        layout17.addWidget(self.joint_edit)
        self.stacked_widget.addWidget(page17)

        # Page 18: MVP
        page18 = QWidget()
        layout18 = QVBoxLayout(page18)
        self.mvp_image = QLabel()
        self.mvp_image.setPixmap(QPixmap("Pictures/ПМК.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout18.addWidget(self.mvp_image)
        layout18.addWidget(QLabel("Пролапс митрального клапана (0 или 1):"))
        self.mvp_edit = QLineEdit()
        layout18.addWidget(self.mvp_edit)
        self.stacked_widget.addWidget(page18)

        # Page 19: Varicose veins
        page19 = QWidget()
        layout19 = QVBoxLayout(page19)
        self.varicose_image = QLabel()
        self.varicose_image.setPixmap(QPixmap("Pictures/Варикоз.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout19.addWidget(self.varicose_image)
        layout19.addWidget(QLabel("Варикоз легкой степени (0 или 1):"))
        self.varicose_light_edit = QLineEdit()
        layout19.addWidget(self.varicose_light_edit)
        layout19.addWidget(QLabel("Варикоз тяжелой степени (0 или 1):"))
        self.varicose_heavy_edit = QLineEdit()
        layout19.addWidget(self.varicose_heavy_edit)
        self.stacked_widget.addWidget(page19)

        # Page 20: Myopia
        page20 = QWidget()
        layout20 = QVBoxLayout(page20)
        self.myopia_image = QLabel()
        self.myopia_image.setPixmap(QPixmap("Pictures/Миопия.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout20.addWidget(self.myopia_image)
        layout20.addWidget(QLabel("Миопия легкой степени (0 или 1):"))
        self.myopia_light_edit = QLineEdit()
        layout20.addWidget(self.myopia_light_edit)
        layout20.addWidget(QLabel("Миопия тяжелой степени (0 или 1):"))
        self.myopia_heavy_edit = QLineEdit()
        layout20.addWidget(self.myopia_heavy_edit)
        self.stacked_widget.addWidget(page20)

        # Page 21: Gallbladder
        page21 = QWidget()
        layout21 = QVBoxLayout(page21)
        self.gallbladder_image = QLabel()
        self.gallbladder_image.setPixmap(QPixmap("Pictures/Желчный пузырь.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout21.addWidget(self.gallbladder_image)
        layout21.addWidget(QLabel("Деформация желчного пузыря (0 или 1):"))
        self.gallbladder_edit = QLineEdit()
        layout21.addWidget(self.gallbladder_edit)
        self.stacked_widget.addWidget(page21)

        # Page 22: GERD
        page22 = QWidget()
        layout22 = QVBoxLayout(page22)
        self.gerd_image = QLabel()
        self.gerd_image.setPixmap(QPixmap("Pictures/ГЭРБ.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout22.addWidget(self.gerd_image)
        layout22.addWidget(QLabel("ГЭРБ (Гастроэзофагеальная рефлюксная болезнь) (0 или 1):"))
        self.gerd_edit = QLineEdit()
        layout22.addWidget(self.gerd_edit)
        self.stacked_widget.addWidget(page22)

        # Page 23: Hypotension
        page23 = QWidget()
        layout23 = QVBoxLayout(page23)
        self.hypotension_image = QLabel()
        self.hypotension_image.setPixmap(QPixmap("Pictures/Гипотензия.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout23.addWidget(self.hypotension_image)
        layout23.addWidget(QLabel("Гипотензия (0 или 1):"))
        self.hypotension_edit = QLineEdit()
        layout23.addWidget(self.hypotension_edit)
        self.stacked_widget.addWidget(page23)

    def update_table(self, df):
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)

        for row_idx, row in df.iterrows():
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_idx, col_idx, item)

    def get_current_page_index(self):
        return self.stacked_widget.currentIndex()

    def set_current_page_index(self, index):
        self.stacked_widget.setCurrentIndex(index)
        if self.get_current_page_index() == 0 or self.get_current_page_index() == 1:
            self.dialog.setFixedSize(300, 200)
        else:
            self.dialog.setFixedSize(950, 700)

    def get_input_values(self):
        age = self.age_edit.text()
        height = self.height_edit.text()
        weight = self.weight_edit.text()
        dst = self.dst_edit.text()
        gms = self.gms_edit.text()
        skin_light = self.skin_light_edit.text()
        skin_heavy = self.skin_heavy_edit.text()
        keloid = self.keloid_edit.text()
        striae = self.striae_edit.text()
        hemorrhages = self.hemorrhages_edit.text()
        hernias = self.hernias_edit.text()
        ptosis = self.ptosis_edit.text()
        tmj = self.tmj_edit.text()
        periodontosis = self.periodontosis_edit.text()
        dolicho = self.dolicho_edit.text()
        kyphosis = self.kyphosis_edit.text()
        chest = self.chest_edit.text()
        flatfeet = self.flatfeet_edit.text()
        valgus = self.valgus_edit.text()
        joint = self.joint_edit.text()
        mvp = self.mvp_edit.text()
        varicose_light = self.varicose_light_edit.text()
        varicose_heavy = self.varicose_heavy_edit.text()
        myopia_light = self.myopia_light_edit.text()
        myopia_heavy = self.myopia_heavy_edit.text()
        gallbladder = self.gallbladder_edit.text()
        gerd = self.gerd_edit.text()
        hypotension = self.hypotension_edit.text()

        return {
            "age": age,
            "height": height,
            "weight": weight,
            "dst": dst,
            "gms": gms,
            "skin_light": skin_light,
            "skin_heavy": skin_heavy,
            "keloid": keloid,
            "striae": striae,
            "hemorrhages": hemorrhages,
            "hernias": hernias,
            "ptosis": ptosis,
            "tmj": tmj,
            "periodontosis": periodontosis,
            "dolicho": dolicho,
            "kyphosis": kyphosis,
            "chest": chest,
            "flatfeet": flatfeet,
            "valgus": valgus,
            "joint": joint,
            "mvp": mvp,
            "varicose_light": varicose_light,
            "varicose_heavy": varicose_heavy,
            "myopia_light": myopia_light,
            "myopia_heavy": myopia_heavy,
            "gallbladder": gallbladder,
            "gerd": gerd,
            "hypotension": hypotension
        }

    def set_input_values(self, values):
        self.age_edit.setText(str(values["age"]))
        self.height_edit.setText(str(values["height"]))
        self.weight_edit.setText(str(values["weight"]))
        self.dst_edit.setText(str(values["dst"]))
        self.gms_edit.setText(str(values["gms"]))
        self.skin_light_edit.setText(str(values["skin_light"]))
        self.skin_heavy_edit.setText(str(values["skin_heavy"]))
        self.keloid_edit.setText(str(values["keloid"]))
        self.striae_edit.setText(str(values["striae"]))
        self.hemorrhages_edit.setText(str(values["hemorrhages"]))
        self.hernias_edit.setText(str(values["hernias"]))
        self.ptosis_edit.setText(str(values["ptosis"]))
        self.tmj_edit.setText(str(values["tmj"]))
        self.periodontosis_edit.setText(str(values["periodontosis"]))
        self.dolicho_edit.setText(str(values["dolicho"]))
        self.kyphosis_edit.setText(str(values["kyphosis"]))
        self.chest_edit.setText(str(values["chest"]))
        self.flatfeet_edit.setText(str(values["flatfeet"]))
        self.valgus_edit.setText(str(values["valgus"]))
        self.joint_edit.setText(str(values["joint"]))
        self.mvp_edit.setText(str(values["mvp"]))
        self.varicose_light_edit.setText(str(values["varicose_light"]))
        self.varicose_heavy_edit.setText(str(values["varicose_heavy"]))
        self.myopia_light_edit.setText(str(values["myopia_light"]))
        self.myopia_heavy_edit.setText(str(values["myopia_heavy"]))
        self.gallbladder_edit.setText(str(values["gallbladder"]))
        self.gerd_edit.setText(str(values["gerd"]))
        self.hypotension_edit.setText(str(values["hypotension"]))

    def clear_inputs(self):
        self.age_edit.clear()
        self.height_edit.clear()
        self.weight_edit.clear()
        self.dst_edit.clear()
        self.gms_edit.clear()
        self.skin_light_edit.clear()
        self.skin_heavy_edit.clear()
        self.keloid_edit.clear()
        self.striae_edit.clear()
        self.hemorrhages_edit.clear()
        self.hernias_edit.clear()
        self.ptosis_edit.clear()
        self.tmj_edit.clear()
        self.periodontosis_edit.clear()
        self.dolicho_edit.clear()
        self.kyphosis_edit.clear()
        self.chest_edit.clear()
        self.flatfeet_edit.clear()
        self.valgus_edit.clear()
        self.joint_edit.clear()
        self.mvp_edit.clear()
        self.varicose_light_edit.clear()
        self.varicose_heavy_edit.clear()
        self.myopia_light_edit.clear()
        self.myopia_heavy_edit.clear()
        self.gallbladder_edit.clear()
        self.gerd_edit.clear()
        self.hypotension_edit.clear()

    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)

    def get_selected_row_index(self):
        selected = self.table.selectedItems()
        if selected:
            return selected[0].row()
        return -1
