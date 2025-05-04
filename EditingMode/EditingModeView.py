from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QTableWidget, QTableWidgetItem,
                               QFileDialog, QMessageBox, QDialog, QFormLayout,
                               QLineEdit, QComboBox, QInputDialog, QSplitter, QListWidget, QGroupBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
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

        self.btn_add_table = QPushButton("Добавить таблицу")
        self.btn_edit_table = QPushButton("Изменить таблицу")
        self.btn_delete_table = QPushButton("Удалить таблицу")

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

        # Группа "Таблица"
        group_table = QGroupBox("Таблица")
        layout_table = QVBoxLayout(group_table)
        layout_table.addWidget(self.btn_add_table)
        #layout_table.addWidget(self.btn_edit_table)
        layout_table.addWidget(self.btn_delete_table)
        left_layout.addWidget(group_table)

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
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        right_layout.addWidget(self.table)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)  # индекс 0 — первый виджет
        splitter.setStretchFactor(1, 4)  # индекс 1 — второй виджет

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

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


