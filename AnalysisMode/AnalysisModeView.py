import os
import sys

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QComboBox, QLabel, QLineEdit, QPushButton, QListWidget,
    QCheckBox, QTableView, QTextEdit, QGridLayout, QScrollArea, QSplitter
)
from PySide6.QtCore import Qt

def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсу """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class AnalysisModeView(QMainWindow):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user

        # Элементы на левой панели
        self.file_path_edit = QLineEdit()
        self.btn_load_local = QPushButton("Загрузить данные")
        self.btn_save_local = QPushButton("Сохранить данные")
        self.btn_load_from_cloud = QPushButton("Загрузить из облака")
        self.btn_save_to_cloud = QPushButton("Сохранить в облако")
        self.btn_filter = QPushButton("Фильтровать данные")
        self.btn_reset_filter = QPushButton("Сбросить фильтр")
        self.columns_list = QListWidget()

        # Вкладки
        self.tabs = QTabWidget()

        # Вкладка "Данные"
        self.tab_data = QWidget()
        self.table_view = QTableView()

        # Вкладка "Статистика"
        self.tab_stats = QWidget()
        self.stats_table = QTableView()
        self.btn_refresh_stats = QPushButton("Обновить статистику")
        self.btn_save_stats = QPushButton("Сохранить статистику")

        # Вкладка "Визуализация"
        self.tab_visual = QWidget()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.plot_type_combo = QComboBox()
        self.btn_plot = QPushButton("Построить график")
        self.btn_export = QPushButton("Экспорт графиков")

        # Вкладка "Анализ"
        self.tab_analysis = QWidget()
        self.analysis_text = QTextEdit()
        self.btn_correlation = QPushButton("Корреляционный анализ")
        self.btn_distribution = QPushButton("Анализ распределений")
        self.btn_outliers = QPushButton("Анализ выбросов")
        self.btn_missing = QPushButton("Анализ пропусков")
        self.btn_cluster = QPushButton("Кластерный анализ")

        # Вкладка "Прогнозирование"
        self.tab_prediction = QWidget()
        self.model_combo = QComboBox()
        self.task_type_combo = QComboBox()
        self.btn_model_settings = QPushButton("Настроить модель")
        self.target_combo = QComboBox()
        self.select_all_checkbox = QCheckBox("Выбрать все признаки")
        self.scroll_area = QScrollArea()
        self.input_container = QWidget()
        self.input_layout = QGridLayout(self.input_container)
        self.btn_train = QPushButton("Обучить модель")
        self.btn_predict = QPushButton("Сделать прогноз")
        self.prediction_result = QLabel("")
        self.model_info = QTextEdit()

        self.init_ui()

        # Меню
        self.create_action = QAction("Создание и пополнение", self)
        self.legend_action = QAction("Памятка по признакам", self)
        self.about_action = QAction("О программе", self)
        self.create_menus()

    def init_ui(self):
        self.setWindowTitle(f"Режим анализа данных - {self.current_user['ФИО']}")
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
        group_actions = QGroupBox("Файл")
        layout_actions = QVBoxLayout(group_actions)
        layout_actions.addWidget(QLabel("Путь к файлу:"))
        layout_actions.addWidget(self.file_path_edit)
        layout_actions.addWidget(self.btn_load_local)
        layout_actions.addWidget(self.btn_save_local)
        layout_actions.addWidget(self.btn_load_from_cloud)
        layout_actions.addWidget(self.btn_save_to_cloud)
        left_layout.addWidget(group_actions)

        # Группа фильтрация
        group_filter = QGroupBox("Фильтрация")
        layout_filter = QVBoxLayout(group_filter)
        layout_filter.addWidget(self.btn_filter)
        layout_filter.addWidget(self.btn_reset_filter)
        left_layout.addWidget(group_filter)

        # Группа столбцы
        group_columns = QGroupBox("Столбцы для визуализации")
        layout_columns = QVBoxLayout(group_columns)
        layout_columns.addWidget(self.columns_list)
        left_layout.addWidget(group_columns)

        # Правая панель с вкладками
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Вкладка "Данные"
        layout_tab_data = QVBoxLayout(self.tab_data)
        layout_tab_data.addWidget(self.table_view)

        # Вкладка "Статистика"
        layout_tab_stats = QVBoxLayout(self.tab_stats)
        self.stats_table.setSortingEnabled(True)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.btn_refresh_stats)
        button_layout.addWidget(self.btn_save_stats)
        layout_tab_stats.addLayout(button_layout)
        layout_tab_stats.addWidget(self.stats_table, stretch=6)

        # Вкладка "Визуализация"
        self.plot_type_combo.addItems(["Гистограмма", "Диаграмма рассеяния по осям", "Точечный график",
                                       "Линейный график", "Круговая диаграмма"])
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_plot)
        btn_layout.addWidget(self.btn_export)
        layout_tab_visual = QVBoxLayout(self.tab_visual)
        layout_tab_visual.addWidget(self.plot_type_combo)
        layout_tab_visual.addLayout(btn_layout)
        layout_tab_visual.addWidget(self.canvas)

        # Вкладка "Анализ"
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setStyleSheet("font-size: 11pt;")
        layout_tab_analysis = QVBoxLayout(self.tab_analysis)


        # Группа кнопок анализа
        analysis_buttons = QHBoxLayout()
        analysis_buttons.addWidget(self.btn_correlation)
        analysis_buttons.addWidget(self.btn_distribution)
        analysis_buttons.addWidget(self.btn_outliers)
        analysis_buttons.addWidget(self.btn_missing)
        analysis_buttons.addWidget(self.btn_cluster)

        layout_tab_analysis.addLayout(analysis_buttons)
        layout_tab_analysis.addWidget(self.analysis_text)

        # Вкладка "Прогнозирование"
        layout_tab_prediction = QVBoxLayout(self.tab_prediction)

        # Группа для выбора типа задачи, модели и целевой переменной
        model_group = QGroupBox("Настройки прогнозирования")
        model_layout = QGridLayout(model_group)
        label_task = QLabel("Задача:")
        label_task.setFixedWidth(50)
        model_layout.addWidget(label_task, 0, 0)
        self.task_type_combo.addItems(["Классификация", "Регрессия"])
        model_layout.addWidget(self.task_type_combo, 0, 1)
        label_model = QLabel("Модель:")
        label_model.setFixedWidth(50)
        model_layout.addWidget(label_model, 0, 2)
        self.model_combo.addItems(
           ["Случайный лес", "Логистическая регрессия", "K-ближайших соседей (KNN)", "Дерево решений"])

        model_layout.addWidget(self.model_combo, 0, 3)
        model_layout.addWidget(self.btn_model_settings, 0, 4)
        model_layout.addWidget(QLabel("Целевой признак:"), 1, 0)
        self.target_combo.setMinimumWidth(200)
        model_layout.addWidget(self.target_combo, 1, 1)
        layout_tab_prediction.addWidget(model_group)

        # Чекбокс "Выбрать все"
        self.select_all_checkbox.setChecked(False)
        layout_tab_prediction.addWidget(self.select_all_checkbox)

        # Область ввода параметров с прокруткой
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
                            QScrollArea { border: 1px solid #ccc; border-radius: 4px; }
                            QLabel { min-width: 50px; font-size: 10pt; }
                            QComboBox, QDoubleSpinBox { 
                                min-width: 40px; 
                                max-width: 100px;
                                font-size: 10pt;
                            }
                        """)
        self.input_layout.setHorizontalSpacing(10)
        self.input_layout.setVerticalSpacing(5)
        self.scroll_area.setWidget(self.input_container)

        layout_tab_prediction.addWidget(QLabel("Выберите признаки и введите значения:"))
        layout_tab_prediction.addWidget(self.scroll_area, stretch=5)

        self.btn_train.setEnabled(False)
        self.btn_predict.setEnabled(False)
        buttons_train_predict_layout = QHBoxLayout()
        buttons_train_predict_layout.addWidget(self.btn_train)
        buttons_train_predict_layout.addWidget(self.btn_predict)
        layout_tab_prediction.addLayout(buttons_train_predict_layout)

        # Блок прогноза
        self.prediction_result.setStyleSheet("font-size: 12pt; font-weight: bold; color: #2c3e50;")
        layout_tab_prediction.addWidget(self.prediction_result)
        self.model_info.setReadOnly(True)
        self.model_info.setStyleSheet("font-size: 10pt;")
        layout_tab_prediction.addWidget(self.model_info)

        # Добавляем вкладки
        self.tabs.addTab(self.tab_data, "Данные")
        self.tabs.addTab(self.tab_stats, "Статистика")
        self.tabs.addTab(self.tab_visual, "Визуализация")
        self.tabs.addTab(self.tab_analysis, "Анализ")
        self.tabs.addTab(self.tab_prediction, "Прогнозирование")

        right_layout.addWidget(self.tabs)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)  # индекс 0 — первый виджет
        splitter.setStretchFactor(1, 2)  # индекс 1 — второй виджет

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def create_menus(self):
        menubar = self.menuBar()
        # Меню "Справка"
        help_menu = menubar.addMenu("Справка")

        # Пункт "Памятка по признакам"
        help_menu.addAction(self.legend_action)

        # Пункт "О программе"
        help_menu.addAction(self.about_action)

        # меню "Режим"
        mode_menu = menubar.addMenu("Режим")

        # Пункт Анализ
        analyze_action = QAction("Анализ", self)
        analyze_action.setCheckable(True)
        analyze_action.setChecked(True)
        mode_menu.addAction(analyze_action)

        # Пункт Создание
        self.create_action.setCheckable(True)
        self.create_action.setChecked(False)
        mode_menu.addAction(self.create_action)
