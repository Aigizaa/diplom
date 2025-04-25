# 1. Импорты
import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import LabelEncoder
import seaborn as sns
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtGui import QAction, QIcon, QPixmap, QGuiApplication
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QComboBox, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QCheckBox, QFileDialog, QTableView, QTextEdit, QMessageBox, QDialog, QFormLayout,
    QDoubleSpinBox, QGridLayout, QScrollArea, QInputDialog, QSizePolicy
)
from PySide6.QtCore import Qt, QAbstractTableModel, QSettings, QSize, Signal

# 2. Вспомогательные функции
def resource_path(relative_path):
    """Получение абсолютного пути к ресурсам"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))

    path = os.path.join(base_path, relative_path)
    return path

# 3. Модели данных
class PandasModel(QAbstractTableModel):
    """Модель для отображения DataFrame в QTableView"""
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            else:
                return str(self._data.index[section])
        return None

    def sort(self, column, order):
        """Базовая сортировка"""
        if 0 <= column < self.columnCount():
            colname = self._data.columns[column]
            self._data = self._data.sort_values(
                colname,
                ascending=(order == Qt.AscendingOrder),
                kind='mergesort'
            )
            self.layoutChanged.emit()

# 4. Диалоговые окна
class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Авторизация")
        self.setFixedSize(500, 550)
        self.move(QGuiApplication.primaryScreen().availableGeometry().center() - self.rect().center())

        icon_path = resource_path("resources/icon2.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)  # Отступы по краям

        # Большая иконка приложения
        icon_label = QLabel()
        try:
            icon_path = resource_path("resources/icon.png")
            icon_pixmap = QPixmap(icon_path).scaled(
                200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(icon_pixmap)
        except Exception as e:
            print(f"Ошибка загрузки иконки: {str(e)}")
            icon_label.setText("Иконка приложения")
            icon_label.setStyleSheet("font-size: 24px;")

        icon_label.setAlignment(Qt.AlignCenter)

        # Название приложения
        title_label = QLabel("Анализатор биомедицинских данных")
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignCenter)

        # Описание приложения
        description = QLabel("""
            <p style='text-align: center; font-size: 14px; color: #34495e;'>
                Программа для анализа клинических показателей пациентов<br>
                с возможностью визуализации данных и статистического анализа
            </p>
            <p style='text-align: center; font-size: 12px; color: #7f8c8d; margin-top: 10px;'>
                Версия 1.0<br>
                Для доступа введите пароль
            </p>
        """)
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)

        # Поля для ввода
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Введите пароль")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet("""
            padding: 8px;
            font-size: 14px;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
        """)

        # Кнопка входа
        btn_login = QPushButton("Войти")
        btn_login.clicked.connect(self.verify_password)
        btn_login.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        layout.addSpacing(10)
        layout.addWidget(icon_label)
        layout.addSpacing(10)
        layout.addWidget(title_label)
        layout.addWidget(description)
        layout.addSpacing(20)
        layout.addWidget(self.password_edit)
        layout.addSpacing(10)
        layout.addWidget(btn_login)
        layout.addStretch()

        # Стиль окна
        self.setStyleSheet("""
            QDialog {
                background-color: #f9f9f9;
                font-family: Arial;
            }
        """)
        self.setLayout(layout)

    def verify_password(self):
        """Проверка пароля"""
        password = self.password_edit.text()
        if password == "a":
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный пароль!")
            self.password_edit.clear()

class FilterDialog(QDialog):
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Фильтрация данных")
        self.columns = columns
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.column_combo = QComboBox()
        self.column_combo.addItems(self.columns)
        form_layout.addRow("Столбец:", self.column_combo)

        self.operator_combo = QComboBox()
        self.operator_combo.addItems([">", ">=", "==", "<=", "<", "!=", "содержит"])
        form_layout.addRow("Оператор:", self.operator_combo)

        self.value_edit = QLineEdit()
        form_layout.addRow("Значение:", self.value_edit)

        layout.addLayout(form_layout)

        self.btn_apply = QPushButton("Применить фильтр")
        self.btn_apply.clicked.connect(self.accept)
        layout.addWidget(self.btn_apply)

        self.setLayout(layout)

    def get_filter(self):
        return {
            'column': self.column_combo.currentText(),
            'operator': self.operator_combo.currentText(),
            'value': self.value_edit.text()
        }

# 5. Главное окно приложения
class MainWindow(QMainWindow):
    # 5.1. Инициализация и настройка UI
    def __init__(self):
        super().__init__()
        self.data = None
        self.original_data = None
        self.setWindowTitle("Анализ биомедицинских данных")
        self.setGeometry(170, 75, 1200, 700)
        icon_path = resource_path("resources/icon.png")
        self.setWindowIcon(QIcon(icon_path))
        self.init_ui()
        self.create_menus()
        self.connect_signals()

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Левая панель управления
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Группа "Действия"
        group_actions = QGroupBox("Действия")
        layout_actions = QVBoxLayout(group_actions)

        self.file_path_edit = QLineEdit()
        self.btn_load = QPushButton("Загрузить Excel")
        self.btn_save = QPushButton("Сохранить данные")
        self.btn_export = QPushButton("Экспорт графиков")
        self.btn_filter = QPushButton("Фильтровать данные")
        self.btn_reset_filter = QPushButton("Сбросить")

        layout_actions.addWidget(QLabel("Путь к файлу:"))
        layout_actions.addWidget(self.file_path_edit)
        layout_actions.addWidget(self.btn_load)
        layout_actions.addWidget(self.btn_save)
        layout_actions.addWidget(self.btn_export)
        layout_actions.addWidget(self.btn_filter)
        layout_actions.addWidget(self.btn_reset_filter)
        left_layout.addWidget(group_actions)

        # Группа "Столбцы"
        group_columns = QGroupBox("Столбцы для визуализации")
        layout_columns = QVBoxLayout(group_columns)

        self.columns_list = QListWidget()
        layout_columns.addWidget(self.columns_list)
        left_layout.addWidget(group_columns)

        # Правая панель с вкладками
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.tabs = QTabWidget()

        # Вкладка "Данные"
        self.tab_data = QWidget()
        self.table_view = QTableView()
        layout_tab_data = QVBoxLayout(self.tab_data)
        layout_tab_data.addWidget(self.table_view)

        # Вкладка "Статистика"
        self.tab_stats = QWidget()
        layout_tab_stats = QVBoxLayout(self.tab_stats)

        # Таблица для статистики
        self.stats_table = QTableView()
        self.stats_table.setSortingEnabled(True)
        layout_tab_stats.addWidget(self.stats_table, stretch=6)

        # Текстовое поле для дополнительной статистики
        self.stats_info_text = QTextEdit()
        self.stats_info_text.setReadOnly(True)
        layout_tab_stats.addWidget(self.stats_info_text, stretch=5)

        # Горизонтальный layout для кнопок
        button_layout = QHBoxLayout()

        # Кнопка для обновления статистики
        self.btn_refresh_stats = QPushButton("Обновить статистику")
        self.btn_refresh_stats.clicked.connect(self.show_stats)
        button_layout.addWidget(self.btn_refresh_stats)

        # Кнопка для сохранения статистики
        self.btn_save_stats = QPushButton("Сохранить статистику")
        self.btn_save_stats.clicked.connect(self.save_stats)
        button_layout.addWidget(self.btn_save_stats)

        # Добавляем layout с кнопками в основной layout
        layout_tab_stats.addLayout(button_layout)

        # Вкладка "Визуализация"
        self.tab_visual = QWidget()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.plot_type_combo = QComboBox()
        self.plot_type_combo.addItems(["Гистограмма", "Боксплот", "Точечный график", "Линейный график"])
        self.btn_plot = QPushButton("Построить график")

        layout_tab_visual = QVBoxLayout(self.tab_visual)
        layout_tab_visual.addWidget(self.plot_type_combo)
        layout_tab_visual.addWidget(self.btn_plot)
        layout_tab_visual.addWidget(self.canvas)

        # Вкладка "Анализ"
        self.tab_analysis = QWidget()
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setStyleSheet("font-size: 11pt;")
        self.btn_analyze = QPushButton("Выполнить анализ")

        layout_tab_analysis = QVBoxLayout(self.tab_analysis)
        layout_tab_analysis.addWidget(self.btn_analyze)
        layout_tab_analysis.addWidget(self.analysis_text)

        # Вкладка "Прогнозирование"
        self.tab_prediction = QWidget()
        layout_tab_prediction = QVBoxLayout(self.tab_prediction)

        # Группа для выбора целевой переменной
        target_group = QGroupBox("Настройки прогнозирования")
        target_layout = QHBoxLayout(target_group)

        target_layout.addWidget(QLabel("Целевой признак:"))
        self.target_combo = QComboBox()
        self.target_combo.setMinimumWidth(200)
        target_layout.addWidget(self.target_combo)
        target_layout.addStretch()

        layout_tab_prediction.addWidget(target_group)

        # Кнопка обучения модели
        self.btn_train = QPushButton("Обучить модель")
        self.btn_train.setEnabled(False)
        layout_tab_prediction.addWidget(self.btn_train)

        # Область ввода параметров с прокруткой
        self.scroll_area = QScrollArea()
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

        self.input_container = QWidget()
        self.input_layout = QGridLayout(self.input_container)
        self.input_layout.setHorizontalSpacing(20)
        self.input_layout.setVerticalSpacing(10)
        self.scroll_area.setWidget(self.input_container)

        layout_tab_prediction.addWidget(QLabel("Введите значения признаков:"))
        layout_tab_prediction.addWidget(self.scroll_area)

        # Блок прогноза
        self.btn_predict = QPushButton("Сделать прогноз")
        self.btn_predict.setEnabled(True)
        self.prediction_result = QLabel("Результат прогноза: ")
        self.prediction_result.setStyleSheet("font-size: 12pt; font-weight: bold; color: #2c3e50;")

        layout_tab_prediction.addWidget(self.btn_predict)
        layout_tab_prediction.addWidget(self.prediction_result)

        # Информация о модели
        self.model_info = QTextEdit()
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
        main_layout.addWidget(left_panel, stretch=1)
        main_layout.addWidget(right_panel, stretch=3)

    def create_menus(self):
        menubar = self.menuBar()
        # Меню "Справка"
        help_menu = menubar.addMenu("Справка")

        # Пункт "Памятка по признакам"
        legend_action = QAction("Памятка по признакам", self)
        legend_action.triggered.connect(self.show_legend)
        help_menu.addAction(legend_action)

        # Пункт "О программе"
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def connect_signals(self):
        """Подключение сигналов к слотам"""
        self.btn_load.clicked.connect(self.load_data)
        self.btn_save.clicked.connect(self.save_data)
        self.btn_export.clicked.connect(self.export_plots)
        self.btn_plot.clicked.connect(self.plot_data)
        self.btn_analyze.clicked.connect(self.run_analysis)
        self.btn_filter.clicked.connect(self.apply_filter)
        self.btn_reset_filter.clicked.connect(self.reset_filter)
        self.btn_train.clicked.connect(self.train_model)
        self.btn_predict.clicked.connect(self.make_prediction)
        self.target_combo.currentTextChanged.connect(self.on_target_changed)

    # 5.2. Методы работы с данными
    def load_data(self):
        """Загрузка данных с обновлением интерфейса прогнозирования"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл Excel", "", "Excel Files (*.xlsx *.xls)"
        )

        if file_path:
            try:
                self.data = pd.read_excel(file_path)
                self.original_data = self.data.copy()
                self.file_path_edit.setText(file_path)

                # Инициализация таблицы данных
                self.model = PandasModel(self.data)
                self.table_view.setModel(self.model)
                self.table_view.setSortingEnabled(True)
                self.table_view.resizeColumnsToContents()

                # Обновление интерфейса
                self.update_columns_list()
                self.show_stats()
                self.update_prediction_combos()

                QMessageBox.information(self, "Успех", "Данные успешно загружены!")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки файла:\n{str(e)}")

    def save_data(self):
        """Сохранение данных в файл"""
        if self.data is None:
            QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить данные", "",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.data.to_csv(file_path, index=False)
                else:
                    self.data.to_excel(file_path, index=False)
                QMessageBox.information(self, "Успех", "Данные успешно сохранены!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения:\n{str(e)}")

    def on_target_changed(self, text):
        """Обработчик изменения целевой переменной"""
        if hasattr(self, 'data') and self.data is not None:
            self.update_input_fields()

    def apply_filter(self):
        """Применение фильтра к данным"""
        if self.data is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите данные!")
            return

        dialog = FilterDialog(self.data.columns.tolist(), self)
        if dialog.exec():
            filter_params = dialog.get_filter()
            try:
                column = filter_params['column']
                operator = filter_params['operator']
                value = filter_params['value']

                if operator == "содержит":
                    self.data = self.data[self.data[column].astype(str).str.contains(value, case=False)]
                else:
                    # Пробуем преобразовать значение в число
                    try:
                        value = float(value) if '.' in value else int(value)
                    except ValueError:
                        pass  # Оставляем как строку, если не число

                    if operator == ">":
                        self.data = self.data[self.data[column] > value]
                    elif operator == ">=":
                        self.data = self.data[self.data[column] >= value]
                    elif operator == "==":
                        self.data = self.data[self.data[column] == value]
                    elif operator == "<=":
                        self.data = self.data[self.data[column] <= value]
                    elif operator == "<":
                        self.data = self.data[self.data[column] < value]
                    elif operator == "!=":
                        self.data = self.data[self.data[column] != value]

                self.update_table_view()
                self.show_stats()
                QMessageBox.information(self, "Успех", "Фильтр успешно применен!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка применения фильтра:\n{str(e)}")

    def reset_filter(self):
        """Сброс фильтров и восстановление оригинальных данных"""
        if self.original_data is not None:
            self.data = self.original_data.copy()
            self.update_table_view()
            self.show_stats()
            QMessageBox.information(self, "Успех", "Фильтры сброшены!")

    def show_stats(self):
        """Отображение статистики данных в таблице на вкладке Статистика"""
        if self.data is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите данные!")
            return

        try:
            stats_df = self.data.describe(include=np.number).round(3)
            # Создаем модель для таблицы
            model = PandasModel(stats_df)
            self.stats_table.setModel(model)
            self.stats_table.resizeColumnsToContents()
            stats_text = "=== ОСНОВНАЯ СТАТИСТИКА ===\n"
            stats_text += f"Всего записей: {len(self.data)}\n"
            missing = self.data.isnull().sum()
            if missing.sum() > 0:
                stats_text += "\n=== ПРОПУЩЕННЫЕ ЗНАЧЕНИЯ ===\n"
                for col, count in missing.items():
                    if count > 0:
                        stats_text += f"{col}: {count} ({count / len(self.data):.1%})\n"

            self.stats_info_text.setPlainText(stats_text)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при расчете статистики:\n{str(e)}")

    def save_stats(self):
        """Сохранение статистики в файл"""
        if self.data is None:
            QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения статистики!")
            return

        try:
            # Получаем статистику (только числовые данные)
            stats_df = self.data.describe(include=np.number).round(3)

            # Диалог сохранения файла
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить статистику",
                "",
                "Excel Files (*.xlsx);;CSV Files (*.csv);;Text Files (*.txt)"
            )

            if file_path:
                if file_path.endswith('.xlsx'):
                    stats_df.to_excel(file_path)
                elif file_path.endswith('.csv'):
                    stats_df.to_csv(file_path)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write("=== ОСНОВНАЯ СТАТИСТИКА ===\n")
                        f.write(stats_df.to_string())
                        f.write("\n\n=== ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ ===\n")
                        f.write(f"Всего записей: {len(self.data)}\n")

                QMessageBox.information(self, "Успех", "Статистика успешно сохранена!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения статистики:\n{str(e)}")

    def run_analysis(self):
        """Анализ данных с выводом информации о самых значимых корреляциях"""
        if self.data is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите данные!")
            return

        try:
            # Выбираем только числовые колонки
            numeric_cols = self.data.select_dtypes(include=np.number).columns
            if len(numeric_cols) < 2:
                self.analysis_text.setPlainText("Недостаточно числовых данных для анализа корреляций")
                return

            # Считаем корреляционную матрицу
            corr_matrix = self.data[numeric_cols].corr()

            # Формируем отчет
            report = []
            report.append("=== АНАЛИЗ КОРРЕЛЯЦИЙ ===")
            report.append(f"Проанализировано {len(numeric_cols)} числовых признаков")
            report.append("\nСамые значимые корреляции (|r| > 0.5):")

            # Собираем все пары с высокой корреляцией
            high_corrs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    corr = corr_matrix.iloc[i, j]
                    if abs(corr) > 0.5:  # Порог значимости
                        high_corrs.append((
                            abs(corr),
                            corr_matrix.columns[i],
                            corr_matrix.columns[j],
                            corr
                        ))

            # Сортируем по убыванию абсолютного значения корреляции
            high_corrs.sort(reverse=True, key=lambda x: x[0])

            # Добавляем в отчет
            if not high_corrs:
                report.append("Не найдено значимых корреляций (|r| > 0.5)")
            else:
                for strength, col1, col2, corr in high_corrs:
                    direction = "прямая" if corr > 0 else "обратная"
                    strength_desc = ""
                    if abs(corr) > 0.8:
                        strength_desc = "очень сильная"
                    elif abs(corr) > 0.6:
                        strength_desc = "сильная"
                    else:
                        strength_desc = "заметная"

                    report.append(
                        f"{col1} ↔ {col2}: r = {corr:.2f} ({strength_desc} {direction} связь)"
                    )

            # Добавляем интерпретацию
            report.append("\n=== ИНТЕРПРЕТАЦИЯ ===")
            report.append("• r > 0.8 - очень сильная зависимость")
            report.append("• 0.6 < r ≤ 0.8 - сильная зависимость")
            report.append("• 0.5 < r ≤ 0.6 - заметная зависимость")
            report.append("• |r| ≤ 0.5 - слабая или отсутствует зависимость")
            report.append("\nПримечание: корреляция не означает причинно-следственную связь!")

            self.analysis_text.setPlainText("\n".join(report))

            # Показываем тепловую карту
            self.show_correlation_heatmap(corr_matrix)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка анализа данных:\n{str(e)}")

    def show_correlation_heatmap(self, corr_matrix):
        """Отображает тепловую карту корреляционной матрицы с полными подписями"""
        # Создаем новое окно
        heatmap_window = QDialog(self)
        heatmap_window.setWindowTitle("Тепловая карта корреляции")
        heatmap_window.setWindowState(Qt.WindowMaximized)  # Разворачиваем на весь экран

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы

        # Создаем фигуру с большим размером
        figure = Figure(figsize=(12, 10), dpi=100)
        canvas = FigureCanvas(figure)

        # Настраиваем тепловую карту
        ax = figure.add_subplot(111)

        # Уменьшаем размер шрифта аннотаций
        annot_size = 8 if len(corr_matrix.columns) > 10 else 10

        # Строим тепловую карту
        sns.heatmap(
            corr_matrix,
            ax=ax,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            center=0,
            linewidths=0.5,
            annot_kws={"size": annot_size},
            cbar_kws={"shrink": 0.8}
        )

        # Настраиваем подписи - поворачиваем и выравниваем
        ax.set_xticklabels(
            ax.get_xticklabels(),
            rotation=45,
            horizontalalignment='right',
            fontsize=10
        )

        ax.set_yticklabels(
            ax.get_yticklabels(),
            rotation=0,
            fontsize=10
        )

        # Увеличиваем отступы для подписей
        ax.figure.subplots_adjust(
            left=0.2,  # Увеличиваем левый отступ для y-меток
            bottom=0.3  # Увеличиваем нижний отступ для x-меток
        )

        # Автоматически подгоняем макет
        figure.tight_layout()

        # Добавляем элементы в layout
        toolbar = NavigationToolbar(canvas, heatmap_window)
        layout.addWidget(toolbar)
        layout.addWidget(canvas)

        # Кнопка сохранения
        btn_save = QPushButton("Сохранить как изображение")
        btn_save.clicked.connect(lambda: self.save_heatmap(figure))
        layout.addWidget(btn_save)

        heatmap_window.setLayout(layout)
        heatmap_window.exec_()

    def save_heatmap(self, figure):
        """Сохраняет тепловую карту как изображение"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить тепловую карту",
            "",
            "PNG Files (*.png);;JPEG Files (*.jpg);;PDF Files (*.pdf)"
        )
        if file_path:
            try:
                figure.savefig(file_path, bbox_inches='tight', dpi=300)
                QMessageBox.information(self, "Успех", "Тепловая карта успешно сохранена!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения:\n{str(e)}")

    # 5.4. Методы визуализации
    def plot_data(self):
        if self.data is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите данные!")
            return

        selected_cols = []
        for i in range(self.columns_list.count()):
            if self.columns_list.item(i).checkState() == Qt.Checked:
                selected_cols.append(self.columns_list.item(i).text())

        if not selected_cols:
            QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один столбец!")
            return

        plot_type = self.plot_type_combo.currentText()
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        try:
            if plot_type == "Гистограмма":
                # Для числовых данных
                num_cols = [col for col in selected_cols
                            if pd.api.types.is_numeric_dtype(self.data[col])]
                if num_cols:
                    self.data[num_cols].hist(ax=ax, bins=15)
                    ax.set_title("Гистограммы числовых данных")
                else:
                    # Для категориальных данных - bar plot
                    cat_cols = [col for col in selected_cols
                                if not pd.api.types.is_numeric_dtype(self.data[col])]
                    if cat_cols:
                        self.data[cat_cols[0]].value_counts().plot(kind='bar', ax=ax)
                        ax.set_title(f"Распределение {cat_cols[0]}")
                    else:
                        QMessageBox.warning(self, "Ошибка", "Нет подходящих данных для гистограммы!")
                        return

            elif plot_type == "Боксплот":
                num_cols = [col for col in selected_cols
                            if pd.api.types.is_numeric_dtype(self.data[col])]
                if num_cols:
                    self.data[num_cols].plot.box(ax=ax)
                    ax.set_title("Боксплоты числовых данных")
                else:
                    QMessageBox.warning(self, "Ошибка", "Боксплоты требуют числовых данных!")
                    return

            elif plot_type == "Точечный график":
                num_cols = [col for col in selected_cols
                            if pd.api.types.is_numeric_dtype(self.data[col])]
                if len(num_cols) >= 2:
                    x, y = num_cols[0], num_cols[1]
                    self.data.plot.scatter(x=x, y=y, ax=ax)
                    ax.set_title(f"{x} vs {y}")
                else:
                    QMessageBox.warning(self, "Ошибка", "Нужно выбрать 2 числовых столбца!")
                    return

            elif plot_type == "Линейный график":
                num_cols = [col for col in selected_cols
                            if pd.api.types.is_numeric_dtype(self.data[col])]
                if num_cols:
                    self.data[num_cols].plot(ax=ax)
                    ax.set_title("Линейные графики")
                else:
                    QMessageBox.warning(self, "Ошибка", "Нет числовых данных для построения!")
                    return

            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка построения графика:\n{str(e)}")

    def export_plots(self):
        """Экспорт графиков в файл"""
        if self.data is None:
            QMessageBox.warning(self, "Ошибка", "Нет данных для экспорта!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт графиков", "",
            "PNG Files (*.png);;PDF Files (*.pdf)"
        )
        if file_path:
            try:
                self.figure.savefig(file_path)
                QMessageBox.information(self, "Успех", "График успешно экспортирован!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта:\n{str(e)}")

    # 5.5. Методы прогнозирования
    def train_model(self):
        """Обучение модели для прогнозирования выбранного признака"""
        if self.data is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите данные!")
            return

        target = self.target_combo.currentText()
        if not target:
            return

        try:
            # Подготовка данных
            X = self.data.drop(columns=[target]).select_dtypes(include=np.number)
            y = self.data[target]

            # Заполнение пропусков
            X = X.fillna(X.median())

            # Разделение на обучающую и тестовую выборки
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Обучение модели
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)

            # Активируем кнопку прогноза
            self.btn_predict.setEnabled(True)

            # Оценка модели
            y_pred = self.model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)

            # Важность признаков
            importances = pd.DataFrame({
                'Признак': X.columns,
                'Важность': self.model.feature_importances_
            }).sort_values('Важность', ascending=False)

            # Вывод информации
            info = [
                f"Модель обучена для прогнозирования: {target}",
                f"Использовано признаков: {len(X.columns)}",
                f"Средняя абсолютная ошибка (MAE): {mae:.4f}",
                "\nВажность признаков:",
                importances.to_string(index=False)
            ]

            self.model_info.setPlainText("\n".join(info))
            self.update_prediction_combos()  # Обновляем поля ввода

            QMessageBox.information(self, "Успех", "Модель успешно обучена!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обучения модели:\n{str(e)}")

    def make_prediction(self):
        """Прогнозирование на основе введенных значений"""
        if not hasattr(self, 'model'):
            QMessageBox.warning(self, "Ошибка", "Сначала обучите модель!")
            return

        try:
            # Собираем введенные значения
            input_data = {}
            for col, widget in self.input_widgets.items():
                if isinstance(widget, QComboBox):
                    input_data[col] = float(widget.currentText())
                else:
                    input_data[col] = widget.value()

            X = pd.DataFrame([input_data])
            prediction = self.model.predict(X)[0]
            target = self.target_combo.currentText()
            self.prediction_result.setText(
                f"Прогнозируемое значение {target}: {prediction:.4f}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка прогнозирования:\n{str(e)}")

    def update_prediction_combos(self):
        """Обновление списка доступных признаков"""
        if self.data is None:
            return

        # Блокируем сигналы во избежание рекурсии
        self.target_combo.blockSignals(True)

        current_target = self.target_combo.currentText()
        self.target_combo.clear()

        numeric_cols = self.data.select_dtypes(include=np.number).columns.tolist()
        self.target_combo.addItems(numeric_cols)

        if current_target in numeric_cols:
            self.target_combo.setCurrentText(current_target)

        self.btn_train.setEnabled(len(numeric_cols) > 0)
        self.btn_predict.setEnabled(True)
        self.target_combo.blockSignals(False)
        self.update_input_fields()

    def update_input_fields(self):
        """Обновление полей"""
        # Очистка предыдущих полей
        for i in reversed(range(self.input_layout.count())):
            widget = self.input_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        self.input_widgets = {}

        if self.data is None or not self.target_combo.currentText():
            return

        target = self.target_combo.currentText()
        features = [col for col in self.data.select_dtypes(include=np.number).columns
                    if col != target]

        # Настройки сетки
        COLS = 4
        row = col = 0

        for feature in features:
            label = QLabel(feature)
            label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
            label.setToolTip(feature)

            if self.data[feature].nunique() < 10:
                widget = QComboBox()
                unique_vals = sorted(self.data[feature].unique())
                widget.addItems(map(str, unique_vals))
                widget.setFixedWidth(40)
            else:
                widget = QDoubleSpinBox()
                widget.setRange(float(self.data[feature].min()),
                                float(self.data[feature].max()))
                widget.setValue(float(self.data[feature].median()))
                widget.setSingleStep(0.1)
                widget.setFixedWidth(40)

            widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.input_widgets[feature] = widget

            self.input_layout.addWidget(label, row, col * 2,
                                        alignment=Qt.AlignLeft | Qt.AlignVCenter)
            self.input_layout.addWidget(widget, row, col * 2 + 1,
                                        alignment=Qt.AlignLeft | Qt.AlignVCenter)

            col += 1
            if col >= COLS:
                col = 0
                row += 1

        # Минимальные отступы
        self.input_layout.setHorizontalSpacing(5)
        self.input_layout.setVerticalSpacing(3)

    def update_table_view(self):
        """Обновление табличного представления данных"""
        if self.data is not None:
            model = PandasModel(self.data)
            self.table_view.setModel(model)
            self.table_view.resizeColumnsToContents()

    def update_columns_list(self):
        """Обновление списка столбцов"""
        self.columns_list.clear()
        if self.data is not None:
            for col in self.data.columns:
                item = QListWidgetItem(col)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.columns_list.addItem(item)

    def show_legend(self):
        """Показывает всплывающее окно с пояснениями к признакам"""
        legend_text = """
        <h3>Пояснения к признакам:</h3>
        <ul>
        <li><b>ДСТ</b> - Дисплазия соединительной ткани (1 - есть, 0 - нет)</li>
        <li><b>Сумма</b> - Общий балл симптомов</li>
        <li><b>ИМТ</b> - Индекс массы тела</li>
        <li><b>ГМС</b> - Гипермобильность суставов (степень)</li>
        <li><b>Кожа легк/тяж</b> - Поражения кожи (легкие/тяжелые)</li>
        <li><b>Келлоид</b> - Келоидные рубцы</li>
        <li><b>Стрии</b> - Растяжки на коже</li>
        <li><b>Геморрагии</b> - Кровоизлияния</li>
        <li><b>ПМК</b> - Пролапс митрального клапана</li>
        <li><b>ГЭРБ</b> - Гастроэзофагеальная рефлюксная болезнь</li>
        <li><b>Гипотенз</b> - Артериальная гипотензия</li>
        </ul>
        """
        msg = QMessageBox()
        msg.setWindowTitle("Памятка по признакам")
        msg.setText(legend_text)
        msg.setTextFormat(Qt.RichText)
        msg.exec_()

    def show_about(self):
        """Информация о программе"""
        QMessageBox.about(self, "О программе",
                          "Анализатор биомедицинских данных v1.0\n"
                          "Для работы с клиническими показателями пациентов")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Создаем и показываем окно авторизации
    login = LoginWindow()
    if login.exec() == QDialog.Accepted:
        # Если авторизация успешна, показываем главное окно
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        # Если авторизация не пройдена, закрываем приложение
        sys.exit()