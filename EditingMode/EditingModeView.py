import sys

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                               QStackedWidget, QMessageBox, QDialog, QFormLayout, QRadioButton,
                               QLineEdit, QComboBox, QInputDialog, QSplitter, QListWidget, QGroupBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QPixmap
import pandas as pd
import os

def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсу """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

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
        self.setWindowTitle(f"Режим сбора данных - {self.current_user['ФИО']}")
        self.setWindowState(Qt.WindowState.WindowMaximized)
        icon_path = resource_path("resources/icon.png")
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
        self.table.setColumnCount(33)
        self.table.setHorizontalHeaderLabels([
            "Врач",
            "Болезнь",
            "Сумма",
            "Возраст",
            "Рост",
            "Вес",
            "ИМТ",
            "ИМТ<25",
            "ГМС(1-9)",
            "ГМС(1-3)",
            "ГМС: легк.степ.",
            "ГМС: тяж.степ.",
            "Кожа: легк.степ.",
            "Кожа: тяж.степ.",
            "Келоидные рубцы",
            "Стрии",
            "Геморрагии",
            "Грыжи",
            "Птозы",
            "Хруст",
            "ВЧС",
            "Парадонтоз",
            "Долихостеномелия",
            "Кифоз/Лордоз",
            "Деф.гр.клетки",
            "Плоскостопие",
            "Вальгус стоп",
            "Хруст суставов",
            "ПМК",
            "Варикоз: легк.степ.",
            "Варикоз: тяж.степ.",
            "Миопия: легк.степ.",
            "Миопия: тяж.степ.",
            "Желч. пузырь",
            "ГЭРБ",
            "Гипотензия"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        right_layout.addWidget(self.table)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)  # индекс 0 — первый виджет
        splitter.setStretchFactor(1, 4)  # индекс 1 — второй виджет

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # Диалоговое окно для добавления/редактирования записи
        self.dialog = QWidget()
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
        create_action = QAction("Сбор данных", self)
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

        # Страница 2: ГМС
        page2 = QWidget()
        layout2 = QVBoxLayout(page2)
        self.gms_image = QLabel()
        self.gms_image.setPixmap(QPixmap("Pictures/ГМС.png").scaled(900, 700, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout2.addWidget(self.gms_image)
        layout2.addWidget(QLabel("Гипермобильность суставов (1-9):"))
        self.gms_edit = QLineEdit()
        layout2.addWidget(self.gms_edit)
        self.stacked_widget.addWidget(page2)

        # Страница 3: Гиперрастяжимость кожи
        page3 = QWidget()
        layout3 = QVBoxLayout(page3)
        self.skin_image = QLabel()
        self.skin_image.setPixmap(QPixmap("Pictures/Кожа.png").scaled(900, 700, Qt.AspectRatioMode.KeepAspectRatio))
        layout3.addWidget(self.skin_image)
        layout3.addWidget(QLabel("Гиперрастяжимость кожи:"))
        self.skin_no_radio = QRadioButton("Нет")
        self.skin_no_radio.setChecked(True)
        self.skin_light_radio = QRadioButton("Легкая степень")
        self.skin_heavy_radio = QRadioButton("Тяжелая степень")
        layout3.addWidget(self.skin_no_radio)
        layout3.addWidget(self.skin_light_radio)
        layout3.addWidget(self.skin_heavy_radio)
        self.stacked_widget.addWidget(page3)

        # Страница 4: Келоид
        page4 = QWidget()
        layout4 = QVBoxLayout(page4)
        self.keloid_image = QLabel()
        self.keloid_image.setPixmap(QPixmap("Pictures/Келоидные рубцы.png").scaled(900, 700, Qt.AspectRatioMode.KeepAspectRatio,
                                                            Qt.TransformationMode.SmoothTransformation))
        layout4.addWidget(self.keloid_image)
        layout4.addWidget(QLabel("Келоидные рубцы:"))
        self.keloid_yes_radio = QRadioButton("Да")
        self.keloid_no_radio = QRadioButton("Нет")
        self.keloid_no_radio.setChecked(True)
        layout4.addWidget(self.keloid_yes_radio)
        layout4.addWidget(self.keloid_no_radio)
        self.stacked_widget.addWidget(page4)

        # Страница 5: Стрии
        page5 = QWidget()
        layout5 = QVBoxLayout(page5)
        self.striae_image = QLabel()
        self.striae_image.setPixmap(QPixmap("Pictures/Стрии.png").scaled(900, 700, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout5.addWidget(self.striae_image)
        layout5.addWidget(QLabel("Стрии:"))
        self.striae_yes_radio = QRadioButton("Да")
        self.striae_no_radio = QRadioButton("Нет")
        self.striae_no_radio.setChecked(True)
        layout5.addWidget(self.striae_yes_radio)
        layout5.addWidget(self.striae_no_radio)
        self.stacked_widget.addWidget(page5)

        # Страница 6: геморрагии
        page6 = QWidget()
        layout6 = QVBoxLayout(page6)
        self.hemorrhages_image = QLabel()
        self.hemorrhages_image.setPixmap(QPixmap("Pictures/Геморрагии.png").scaled(900, 700, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout6.addWidget(self.hemorrhages_image)
        layout6.addWidget(QLabel("Геморрагии:"))
        self.hemorrhages_yes_radio = QRadioButton("Да")
        self.hemorrhages_no_radio = QRadioButton("Нет")
        self.hemorrhages_no_radio.setChecked(True)
        layout6.addWidget(self.hemorrhages_yes_radio)
        layout6.addWidget(self.hemorrhages_no_radio)
        self.stacked_widget.addWidget(page6)

        # Страница 7: грыжи
        page7 = QWidget()
        layout7 = QVBoxLayout(page7)
        self.hernias_image = QLabel()
        self.hernias_image.setPixmap(QPixmap("Pictures/Грыжи.png").scaled(900, 700, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout7.addWidget(self.hernias_image)
        layout7.addWidget(QLabel("Грыжи:"))
        self.hernias_yes_radio = QRadioButton("Да")
        self.hernias_no_radio = QRadioButton("Нет")
        self.hernias_no_radio.setChecked(True)
        layout7.addWidget(self.hernias_yes_radio)
        layout7.addWidget(self.hernias_no_radio)
        self.stacked_widget.addWidget(page7)

        # Страница 8: Птозы
        page8 = QWidget()
        layout8 = QVBoxLayout(page8)
        self.ptosis_image = QLabel()
        self.ptosis_image.setPixmap(QPixmap("Pictures/Птозы.png").scaled(900, 700, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout8.addWidget(self.ptosis_image)
        layout8.addWidget(QLabel("Птозы:"))
        self.ptosis_yes_radio = QRadioButton("Да")
        self.ptosis_no_radio = QRadioButton("Нет")
        self.ptosis_no_radio.setChecked(True)
        layout8.addWidget(self.ptosis_yes_radio)
        layout8.addWidget(self.ptosis_no_radio)
        self.stacked_widget.addWidget(page8)

        # Страница 9: хруст вчс
        page9 = QWidget()
        layout9 = QVBoxLayout(page9)
        self.tmj_image = QLabel()
        self.tmj_image.setPixmap(QPixmap("Pictures/Хруст ВЧС.png").scaled(900, 700, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout9.addWidget(self.tmj_image)
        layout9.addWidget(QLabel("Хруст ВЧС:"))
        self.tmj_yes_radio = QRadioButton("Да")
        self.tmj_no_radio = QRadioButton("Нет")
        self.tmj_no_radio.setChecked(True)
        layout9.addWidget(self.tmj_yes_radio)
        layout9.addWidget(self.tmj_no_radio)
        self.stacked_widget.addWidget(page9)

        # Страница 10: парадонтит
        page10 = QWidget()
        layout10 = QVBoxLayout(page10)
        self.periodontosis_image = QLabel()
        self.periodontosis_image.setPixmap(QPixmap("Pictures/Парадонтоз.png").scaled(900, 700, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout10.addWidget(self.periodontosis_image)
        layout10.addWidget(QLabel("Парадонтоз:"))
        self.periodontosis_yes_radio = QRadioButton("Да")
        self.periodontosis_no_radio = QRadioButton("Нет")
        self.periodontosis_no_radio.setChecked(True)
        layout10.addWidget(self.periodontosis_yes_radio)
        layout10.addWidget(self.periodontosis_no_radio)
        self.stacked_widget.addWidget(page10)

        # Страница 11: долихостеномелия
        page11 = QWidget()
        layout11 = QVBoxLayout(page11)
        self.dolicho_image = QLabel()
        self.dolicho_image.setPixmap(QPixmap("Pictures/Долихостеномелия.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout11.addWidget(self.dolicho_image)
        layout11.addWidget(QLabel("Долихостеномелия:"))
        self.dolicho_yes_radio = QRadioButton("Да")
        self.dolicho_no_radio = QRadioButton("Нет")
        self.dolicho_no_radio.setChecked(True)
        layout11.addWidget(self.dolicho_yes_radio)
        layout11.addWidget(self.dolicho_no_radio)
        self.stacked_widget.addWidget(page11)

        # Страница 12: кифоз/лордоз
        page12 = QWidget()
        layout12 = QVBoxLayout(page12)
        self.kyphosis_image = QLabel()
        self.kyphosis_image.setPixmap(QPixmap("Pictures/Кифоз_лордоз.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout12.addWidget(self.kyphosis_image)
        layout12.addWidget(QLabel("Гиперкифоз/гиперлордоз:"))
        self.kyphosis_yes_radio = QRadioButton("Да")
        self.kyphosis_no_radio = QRadioButton("Нет")
        self.kyphosis_no_radio.setChecked(True)
        layout12.addWidget(self.kyphosis_yes_radio)
        layout12.addWidget(self.kyphosis_no_radio)
        self.stacked_widget.addWidget(page12)

        # Страница 13: деформация грудной клетки
        page13 = QWidget()
        layout13 = QVBoxLayout(page13)
        self.chest_image = QLabel()
        self.chest_image.setPixmap(QPixmap("Pictures/Деф гр клет.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout13.addWidget(self.chest_image)
        layout13.addWidget(QLabel("Деформация грудной клетки:"))
        self.chest_yes_radio = QRadioButton("Да")
        self.chest_no_radio = QRadioButton("Нет")
        self.chest_no_radio.setChecked(True)
        layout13.addWidget(self.chest_yes_radio)
        layout13.addWidget(self.chest_no_radio)
        self.stacked_widget.addWidget(page13)

        # Страница 14: плоскостопие
        page14 = QWidget()
        layout14 = QVBoxLayout(page14)
        self.flatfeet_image = QLabel()
        self.flatfeet_image.setPixmap(QPixmap("Pictures/Плоскостопие.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout14.addWidget(self.flatfeet_image)
        layout14.addWidget(QLabel("Плоскостопие:"))
        self.flatfeet_yes_radio = QRadioButton("Да")
        self.flatfeet_no_radio = QRadioButton("Нет")
        self.flatfeet_no_radio.setChecked(True)
        layout14.addWidget(self.flatfeet_yes_radio)
        layout14.addWidget(self.flatfeet_no_radio)
        self.stacked_widget.addWidget(page14)

        # Страница 15: вальгус
        page15 = QWidget()
        layout15 = QVBoxLayout(page15)
        self.valgus_image = QLabel()
        self.valgus_image.setPixmap(QPixmap("Pictures/Вальгус.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout15.addWidget(self.valgus_image)
        layout15.addWidget(QLabel("Вальгус стоп:"))
        self.valgus_yes_radio = QRadioButton("Да")
        self.valgus_no_radio = QRadioButton("Нет")
        self.valgus_no_radio.setChecked(True)
        layout15.addWidget(self.valgus_yes_radio)
        layout15.addWidget(self.valgus_no_radio)
        self.stacked_widget.addWidget(page15)

        # Страница 16: хруст суставов
        page16 = QWidget()
        layout16 = QVBoxLayout(page16)
        self.joint_image = QLabel()
        self.joint_image.setPixmap(QPixmap("Pictures/Хруст_в_суставах.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout16.addWidget(self.joint_image)
        layout16.addWidget(QLabel("Хруст суставов:"))
        self.joint_yes_radio = QRadioButton("Да")
        self.joint_no_radio = QRadioButton("Нет")
        self.joint_no_radio.setChecked(True)
        layout16.addWidget(self.joint_yes_radio)
        layout16.addWidget(self.joint_no_radio)
        self.stacked_widget.addWidget(page16)

        # Страница 17: ПМК
        page17 = QWidget()
        layout17 = QVBoxLayout(page17)
        self.mvp_image = QLabel()
        self.mvp_image.setPixmap(QPixmap("Pictures/ПМК.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout17.addWidget(self.mvp_image)
        layout17.addWidget(QLabel("Пролапс митрального клапана:"))
        self.mvp_yes_radio = QRadioButton("Да")
        self.mvp_no_radio = QRadioButton("Нет")
        self.mvp_no_radio.setChecked(True)
        layout17.addWidget(self.mvp_yes_radio)
        layout17.addWidget(self.mvp_no_radio)
        self.stacked_widget.addWidget(page17)

        # Страница 18: Varicose veins
        page18 = QWidget()
        layout18 = QVBoxLayout(page18)
        self.varicose_image = QLabel()
        self.varicose_image.setPixmap(QPixmap("Pictures/Варикоз.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout18.addWidget(self.varicose_image)
        layout18.addWidget(QLabel("Варикоз:"))
        self.varicose_no_radio = QRadioButton("Нет")
        self.varicose_light_radio = QRadioButton("Легкая степень")
        self.varicose_heavy_radio = QRadioButton("Тяжелая степень")
        self.varicose_no_radio.setChecked(True)
        layout18.addWidget(self.varicose_no_radio)
        layout18.addWidget(self.varicose_light_radio)
        layout18.addWidget(self.varicose_heavy_radio)
        self.stacked_widget.addWidget(page18)

        # Страница 19: миопия
        page19 = QWidget()
        layout19 = QVBoxLayout(page19)
        self.myopia_image = QLabel()
        self.myopia_image.setPixmap(QPixmap("Pictures/Миопия.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout19.addWidget(self.myopia_image)
        layout19.addWidget(QLabel("Миопия:"))
        self.myopia_no_radio = QRadioButton("Нет")
        self.myopia_light_radio = QRadioButton("Легкая степень")
        self.myopia_heavy_radio = QRadioButton("Тяжелая степень")
        self.myopia_no_radio.setChecked(True)
        layout19.addWidget(self.myopia_no_radio)
        layout19.addWidget(self.myopia_light_radio)
        layout19.addWidget(self.myopia_heavy_radio)
        self.stacked_widget.addWidget(page19)

        # Страница 20: желчный пузырь
        page20 = QWidget()
        layout20 = QVBoxLayout(page20)
        self.gallbladder_image = QLabel()
        self.gallbladder_image.setPixmap(QPixmap("Pictures/Желчный пузырь.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout20.addWidget(self.gallbladder_image)
        layout20.addWidget(QLabel("Деформация желчного пузыря:"))
        self.gallbladder_yes_radio = QRadioButton("Да")
        self.gallbladder_no_radio = QRadioButton("Нет")
        self.gallbladder_no_radio.setChecked(True)
        layout20.addWidget(self.gallbladder_yes_radio)
        layout20.addWidget(self.gallbladder_no_radio)
        self.stacked_widget.addWidget(page20)

        # Страница 21: ГЭРБ
        page21 = QWidget()
        layout21 = QVBoxLayout(page21)
        self.gerd_image = QLabel()
        self.gerd_image.setPixmap(QPixmap("Pictures/ГЭРБ.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout21.addWidget(self.gerd_image)
        layout21.addWidget(QLabel("ГЭРБ (Гастроэзофагеальная рефлюксная болезнь):"))
        self.gerd_yes_radio = QRadioButton("Да")
        self.gerd_no_radio = QRadioButton("Нет")
        self.gerd_no_radio.setChecked(True)
        layout21.addWidget(self.gerd_yes_radio)
        layout21.addWidget(self.gerd_no_radio)
        self.stacked_widget.addWidget(page21)

        # Страница 22: гипотензия
        page22 = QWidget()
        layout22 = QVBoxLayout(page22)
        self.hypotension_image = QLabel()
        self.hypotension_image.setPixmap(QPixmap("Pictures/Гипотензия.png").scaled(900, 900, Qt.AspectRatioMode.KeepAspectRatio,
                                                                    Qt.TransformationMode.SmoothTransformation))
        layout22.addWidget(self.hypotension_image)
        layout22.addWidget(QLabel("Гипотензия:"))
        self.hypotension_yes_radio = QRadioButton("Да")
        self.hypotension_no_radio = QRadioButton("Нет")
        self.hypotension_no_radio.setChecked(True)
        layout22.addWidget(self.hypotension_yes_radio)
        layout22.addWidget(self.hypotension_no_radio)
        self.stacked_widget.addWidget(page22)

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
        if self.get_current_page_index() == 0:
            self.dialog.setFixedSize(300, 200)
        else:
            self.dialog.setFixedSize(950, 700)

    def get_input_values(self):
        age = self.age_edit.text()
        height = self.height_edit.text()
        weight = self.weight_edit.text()
        gms = self.gms_edit.text()

        if self.skin_no_radio.isChecked():
            skin_light = 0
            skin_heavy = 0
        elif self.skin_light_radio.isChecked():
            skin_light = 1
            skin_heavy = 0
        else:
            skin_light = 0
            skin_heavy = 1

        keloid = 1 if self.keloid_yes_radio.isChecked() else 0
        striae = 1 if self.striae_yes_radio.isChecked() else 0
        hemorrhages = 1 if self.hemorrhages_yes_radio.isChecked() else 0
        hernias = 1 if self.hernias_yes_radio.isChecked() else 0
        ptosis = 1 if self.ptosis_yes_radio.isChecked() else 0
        tmj = 1 if self.tmj_yes_radio.isChecked() else 0
        periodontosis = 1 if self.periodontosis_yes_radio.isChecked() else 0
        dolicho = 1 if self.dolicho_yes_radio.isChecked() else 0
        kyphosis = 1 if self.kyphosis_yes_radio.isChecked() else 0
        chest = 1 if self.chest_yes_radio.isChecked() else 0
        flatfeet = 1 if self.flatfeet_yes_radio.isChecked() else 0
        valgus = 1 if self.valgus_yes_radio.isChecked() else 0
        joint = 1 if self.joint_yes_radio.isChecked() else 0
        mvp = 1 if self.mvp_yes_radio.isChecked() else 0

        if self.varicose_no_radio.isChecked():
            varicose_light = 0
            varicose_heavy = 0
        elif self.varicose_light_radio.isChecked():
            varicose_light = 1
            varicose_heavy = 0
        else:
            varicose_light = 0
            varicose_heavy = 1

        if self.myopia_no_radio.isChecked():
            myopia_light = 0
            myopia_heavy = 0
        elif self.myopia_light_radio.isChecked():
            myopia_light = 1
            myopia_heavy = 0
        else:
            myopia_light = 0
            myopia_heavy = 1

        gallbladder = 1 if self.gallbladder_yes_radio.isChecked() else 0
        gerd = 1 if self.gerd_yes_radio.isChecked() else 0
        hypotension = 1 if self.hypotension_yes_radio.isChecked() else 0

        return {
            "age": age,
            "height": height,
            "weight": weight,
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
        self.gms_edit.setText(str(values["gms"]))

        if values["skin_light"] == 1:
            self.skin_light_radio.setChecked(True)
        if values["skin_heavy"] == 1:
            self.skin_heavy_radio.setChecked(True)
        if values["skin_heavy"] == 0 and values["skin_light"] == 0:
            self.skin_no_radio.setChecked(True)

        self.keloid_yes_radio.setChecked(True) if values["keloid"] == 1 else self.keloid_no_radio.setChecked(True)
        self.striae_yes_radio.setChecked(True) if values["striae"] == 1 else self.striae_no_radio.setChecked(True)
        self.hemorrhages_yes_radio.setChecked(True) if values["hemorrhages"] == 1 else self.hemorrhages_no_radio.setChecked(True)
        self.hernias_yes_radio.setChecked(True) if values["hernias"] == 1 else self.hernias_no_radio.setChecked(True)
        self.ptosis_yes_radio.setChecked(True) if values["ptosis"] == 1 else self.ptosis_no_radio.setChecked(True)
        self.tmj_yes_radio.setChecked(True) if values["tmj"] == 1 else self.tmj_no_radio.setChecked(True)
        self.periodontosis_yes_radio.setChecked(True) if values["periodontosis"] == 1 else self.periodontosis_no_radio.setChecked(True)
        self.dolicho_yes_radio.setChecked(True) if values["dolicho"] == 1 else self.dolicho_no_radio.setChecked(True)
        self.kyphosis_yes_radio.setChecked(True) if values["kyphosis"] == 1 else self.kyphosis_no_radio.setChecked(True)
        self.chest_yes_radio.setChecked(True) if values["chest"] == 1 else self.chest_no_radio.setChecked(True)
        self.flatfeet_yes_radio.setChecked(True) if values["flatfeet"] == 1 else self.flatfeet_no_radio.setChecked(True)
        self.valgus_yes_radio.setChecked(True) if values["valgus"] == 1 else self.valgus_no_radio.setChecked(True)
        self.joint_yes_radio.setChecked(True) if values["joint"] == 1 else self.joint_no_radio.setChecked(True)
        self.mvp_yes_radio.setChecked(True) if values["mvp"] == 1 else self.mvp_no_radio.setChecked(True)

        if values["varicose_light"] == 1:
            self.varicose_light_radio.setChecked(True)
        if values["varicose_heavy"] == 1:
            self.varicose_heavy_radio.setChecked(True)
        if values["varicose_light"] == 0 and values["varicose_heavy"] == 0:
            self.varicose_no_radio.setChecked(True)

        if values["myopia_light"] == 1:
            self.myopia_light_radio.setChecked(True)
        if values["myopia_heavy"] == 1:
            self.myopia_heavy_radio.setChecked(True)
        if values["myopia_light"] == 0 and values["myopia_heavy"] == 0:
            self.myopia_no_radio.setChecked(True)

        self.gallbladder_yes_radio.setChecked(True) if values["gallbladder"] == 1 else self.gallbladder_no_radio.setChecked(True)
        self.gerd_yes_radio.setChecked(True) if values["gerd"] == 1 else self.gerd_no_radio.setChecked(True)
        self.hypotension_yes_radio.setChecked(True) if values["hypotension"] == 1 else self.hypotension_no_radio.setChecked(True)

    def clear_inputs(self):
        self.age_edit.clear()
        self.height_edit.clear()
        self.weight_edit.clear()
        self.gms_edit.clear()
        self.skin_no_radio.setChecked(True)
        self.skin_light_radio.setChecked(False)
        self.skin_heavy_radio.setChecked(False)
        self.keloid_yes_radio.setChecked(False)
        self.keloid_no_radio.setChecked(True)
        self.striae_yes_radio.setChecked(False)
        self.striae_no_radio.setChecked(True)
        self.hemorrhages_yes_radio.setChecked(False)
        self.hemorrhages_no_radio.setChecked(True)
        self.hernias_yes_radio.setChecked(False)
        self.hernias_no_radio.setChecked(True)
        self.ptosis_yes_radio.setChecked(False)
        self.ptosis_no_radio.setChecked(True)
        self.tmj_yes_radio.setChecked(False)
        self.tmj_no_radio.setChecked(True)
        self.periodontosis_yes_radio.setChecked(False)
        self.periodontosis_no_radio.setChecked(True)
        self.dolicho_yes_radio.setChecked(False)
        self.dolicho_no_radio.setChecked(True)
        self.kyphosis_yes_radio.setChecked(False)
        self.kyphosis_no_radio.setChecked(True)
        self.chest_yes_radio.setChecked(False)
        self.chest_no_radio.setChecked(True)
        self.flatfeet_yes_radio.setChecked(False)
        self.flatfeet_no_radio.setChecked(True)
        self.valgus_yes_radio.setChecked(False)
        self.valgus_no_radio.setChecked(True)
        self.joint_yes_radio.setChecked(False)
        self.joint_no_radio.setChecked(True)
        self.mvp_yes_radio.setChecked(False)
        self.mvp_no_radio.setChecked(True)
        self.varicose_light_radio.setChecked(False)
        self.varicose_heavy_radio.setChecked(False)
        self.varicose_no_radio.setChecked(True)
        self.myopia_light_radio.setChecked(False)
        self.myopia_no_radio.setChecked(True)
        self.myopia_heavy_radio.setChecked(False)
        self.gallbladder_yes_radio.setChecked(False)
        self.gallbladder_no_radio.setChecked(True)
        self.gallbladder_yes_radio.setChecked(False)
        self.gallbladder_no_radio.setChecked(True)
        self.hypotension_yes_radio.setChecked(False)
        self.hypotension_no_radio.setChecked(True)

    def show_error(self, message):
        QMessageBox.critical(self, "Ошибка", message)

    def show_msg(self, message):
        QMessageBox.information(self, "Успех", message)

    def get_selected_row_index(self):
        selected = self.table.selectedItems()
        if selected:
            return selected[0].row()
        return -1
