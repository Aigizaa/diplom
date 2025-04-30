# 1. Импорты
import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, accuracy_score
from sklearn.preprocessing import LabelEncoder
import seaborn as sns
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QComboBox, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QCheckBox, QFileDialog, QTableView, QTextEdit, QMessageBox, QDialog,
    QDoubleSpinBox, QGridLayout, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt
from PandasModel import PandasModel
from FilterDialog import FilterDialog
from ModelSettingsDialog import ModelSettingsDialog

# 2. Вспомогательные функции
def resource_path(relative_path):
    """Получение абсолютного пути к ресурсам"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))

    path = os.path.join(base_path, relative_path)
    return path

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
        self.btn_filter = QPushButton("Фильтровать данные")
        self.btn_reset_filter = QPushButton("Сбросить")

        layout_actions.addWidget(QLabel("Путь к файлу:"))
        layout_actions.addWidget(self.file_path_edit)
        layout_actions.addWidget(self.btn_load)
        layout_actions.addWidget(self.btn_save)
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
        self.plot_type_combo.addItems(["Гистограмма", "Диаграмма рассеяния по осям", "Точечный график", "Линейный график", "Круговая диаграмма"])
        self.btn_plot = QPushButton("Построить график")
        self.btn_export = QPushButton("Экспорт графиков")  # Перенесена сюда кнопка экспорта
        layout_tab_visual = QVBoxLayout(self.tab_visual)
        layout_tab_visual.addWidget(self.plot_type_combo)
        layout_tab_visual.addWidget(self.btn_plot)
        layout_tab_visual.addWidget(self.btn_export)
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

        # Группа для выбора модели и целевой переменной
        model_group = QGroupBox("Настройки прогнозирования")
        model_layout = QGridLayout(model_group)
        model_layout.addWidget(QLabel("Модель:"), 0, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems(
            ["Случайный лес", "Логистическая регрессия", "Линейная регрессия", "K-ближайших соседей (KNN)",
             "Дерево решений"])
        model_layout.addWidget(self.model_combo, 0, 1)

        self.btn_model_settings = QPushButton("Настроить модель")
        self.btn_model_settings.clicked.connect(self.show_model_settings)
        model_layout.addWidget(self.btn_model_settings, 0, 2)

        model_layout.addWidget(QLabel("Целевой признак:"), 1, 0)
        self.target_combo = QComboBox()
        self.target_combo.setMinimumWidth(200)
        model_layout.addWidget(self.target_combo, 1, 1)

        layout_tab_prediction.addWidget(model_group)

        # Чекбокс "Выбрать все"
        self.select_all_checkbox = QCheckBox("Выбрать все признаки")
        self.select_all_checkbox.setChecked(False)
        layout_tab_prediction.addWidget(self.select_all_checkbox)

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
        self.input_layout.setHorizontalSpacing(10)
        self.input_layout.setVerticalSpacing(5)
        self.scroll_area.setWidget(self.input_container)

        layout_tab_prediction.addWidget(QLabel("Выберите признаки и введите значения:"))
        layout_tab_prediction.addWidget(self.scroll_area, stretch=5)

        # Кнопка обучения модели
        self.btn_train = QPushButton("Обучить модель")
        self.btn_train.setEnabled(False)
        layout_tab_prediction.addWidget(self.btn_train)

        # Блок прогноза
        self.btn_predict = QPushButton("Сделать прогноз")
        self.btn_predict.setEnabled(False)
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
        """Загрузка данных из файла (Excel или CSV) с обновлением интерфейса"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть файл данных",
            "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv)"
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
                QMessageBox.warning(self, "Ошибка", "Неподдерживаемый формат файла!")
                return

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
        heatmap_window.exec()

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

        try:
            if plot_type == "Гистограмма":
                ax = self.figure.add_subplot(111)
                num_cols = [col for col in selected_cols if pd.api.types.is_numeric_dtype(self.data[col])]
                if num_cols:
                    self.data[num_cols].hist(ax=ax, bins=15)
                    ax.set_title("Гистограммы числовых данных")
                else:
                    cat_cols = [col for col in selected_cols if not pd.api.types.is_numeric_dtype(self.data[col])]
                    if cat_cols:
                        self.data[cat_cols[0]].value_counts().plot(kind='bar', ax=ax)
                        ax.set_title(f"Распределение {cat_cols[0]}")
                    else:
                        QMessageBox.warning(self, "Ошибка", "Нет подходящих данных для гистограммы!")
                        return

            elif plot_type == "Диаграмма рассеяния по осям":
                num_cols = [col for col in selected_cols if pd.api.types.is_numeric_dtype(self.data[col])]
                if num_cols:
                    for idx, col in enumerate(num_cols):
                        ax = self.figure.add_subplot(1, len(num_cols), idx + 1)
                        ax.plot(self.data[col], 'o', markersize=4)
                        ax.set_title(col)
                        ax.set_xlabel("Индекс")
                        ax.set_ylabel(col)
                else:
                    QMessageBox.warning(self, "Ошибка", "Диаграмма требует числовых данных!")
                    return

            elif plot_type == "Точечный график":
                ax = self.figure.add_subplot(111)
                num_cols = [col for col in selected_cols if pd.api.types.is_numeric_dtype(self.data[col])]
                if len(num_cols) >= 2:
                    x, y = num_cols[0], num_cols[1]
                    self.data.plot.scatter(x=x, y=y, ax=ax)
                    ax.set_title(f"{x} vs {y}")
                else:
                    QMessageBox.warning(self, "Ошибка", "Нужно выбрать 2 числовых столбца!")
                    return

            elif plot_type == "Линейный график":
                ax = self.figure.add_subplot(111)
                num_cols = [col for col in selected_cols if pd.api.types.is_numeric_dtype(self.data[col])]
                if num_cols:
                    self.data[num_cols].plot(ax=ax)
                    ax.set_title("Линейные графики")
                else:
                    QMessageBox.warning(self, "Ошибка", "Нет числовых данных для построения!")
                    return

            elif plot_type == "Круговая диаграмма":
                n = len(selected_cols)
                if n == 0:
                    QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один столбец!")
                    return

                for idx, col in enumerate(selected_cols):
                    ax = self.figure.add_subplot(1, n, idx + 1)
                    if pd.api.types.is_numeric_dtype(self.data[col]):
                        unique_values = self.data[col].dropna().unique()
                        if set(unique_values).issubset({0, 1}):
                            counts = self.data[col].value_counts()
                            labels = ['0', '1']
                            ax.pie(counts, labels=labels, autopct='%1.1f%%')
                            ax.set_title(f"{col} (0/1)")
                        else:
                            counts, bins = np.histogram(self.data[col].dropna(), bins=5)
                            labels = [f"{bins[i]:.1f}-{bins[i + 1]:.1f}" for i in range(len(counts))]
                            ax.pie(counts, labels=labels, autopct='%1.1f%%')
                            ax.set_title(f"{col}")
                    else:
                        counts = self.data[col].value_counts()
                        ax.pie(counts, labels=counts.index, autopct='%1.1f%%')
                        ax.set_title(f"{col}")

            self.figure.tight_layout()
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

    def show_model_settings(self):
        """Показывает диалог настроек модели"""
        model_type = self.model_combo.currentText()
        dialog = ModelSettingsDialog(model_type, self)
        if dialog.exec():
            self.model_settings = dialog.get_settings()

    # 5.5. Методы прогнозирования
    def train_model(self):
        """Модифицированный метод обучения модели"""
        if self.data is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите данные!")
            return

        target = self.target_combo.currentText()
        if not target:
            return

        try:
            # Получаем только выбранные признаки
            selected_features = [feature for feature, widgets in self.feature_widgets.items()
                                 if widgets['checkbox'].isChecked()]

            if not selected_features:
                QMessageBox.warning(self, "Ошибка", "Выберите хотя бы один признак!")
                return

            # Подготовка данных только с выбранными признаками
            X = self.data[selected_features]
            y = self.data[target]

            # Заполнение пропусков
            X = X.fillna(X.median())

            # Разделение на обучающую и тестовую выборки
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Определяем, регрессия или классификация
            is_classification = not pd.api.types.is_numeric_dtype(y)

            # Если это классификация, преобразуем метки
            if is_classification:
                le = LabelEncoder()
                y_train = le.fit_transform(y_train)
                y_test = le.transform(y_test)

            # Получаем тип модели и ее настройки
            model_type = self.model_combo.currentText()
            settings = getattr(self, 'model_settings', {})

            # Создаем модель в зависимости от выбранного типа
            if model_type == "Случайный лес":
                if is_classification:
                    self.model = RandomForestClassifier(
                        n_estimators=settings.get('n_estimators', 100),
                        max_depth=settings.get('max_depth', None),
                        min_samples_split=settings.get('min_samples_split', 2),
                        random_state=42
                    )
                else:
                    self.model = RandomForestRegressor(
                        n_estimators=settings.get('n_estimators', 100),
                        max_depth=settings.get('max_depth', None),
                        min_samples_split=settings.get('min_samples_split', 2),
                        random_state=42
                    )

            elif model_type == "Логистическая регрессия":
                if not is_classification:
                    QMessageBox.warning(self, "Ошибка", "Логистическая регрессия предназначена для классификации!")
                    return
                self.model = LogisticRegression(
                    C=settings.get('C', 1.0),
                    max_iter=settings.get('max_iter', 1000),
                    random_state=42
                )

            elif model_type == "Линейная регрессия":
                if is_classification:
                    QMessageBox.warning(self, "Ошибка", "Линейная регрессия предназначена для регрессии!")
                    return
                self.model = LinearRegression(
                    fit_intercept=settings.get('fit_intercept', True)
                )

            elif model_type == "K-ближайших соседей (KNN)":
                if is_classification:
                    self.model = KNeighborsClassifier(
                        n_neighbors=settings.get('n_neighbors', 5),
                        weights=settings.get('weights', 'uniform')
                    )
                else:
                    self.model = KNeighborsRegressor(
                        n_neighbors=settings.get('n_neighbors', 5),
                        weights=settings.get('weights', 'uniform')
                    )

            elif model_type == "Дерево решений":
                if is_classification:
                    self.model = DecisionTreeClassifier(
                        max_depth=settings.get('max_depth', None),
                        min_samples_split=settings.get('min_samples_split', 2),
                        random_state=42
                    )
                else:
                    self.model = DecisionTreeRegressor(
                        max_depth=settings.get('max_depth', None),
                        min_samples_split=settings.get('min_samples_split', 2),
                        random_state=42
                    )

            # Обучение модели
            self.model.fit(X_train, y_train)

            # Активируем кнопку прогноза
            self.btn_predict.setEnabled(True)

            # Оценка модели
            y_pred = self.model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)

            # Формируем информацию о модели
            info = [
                f"Модель: {model_type}",
                f"Тип: {'Классификация' if is_classification else 'Регрессия'}",
                f"Целевой признак: {target}",
                f"Использовано признаков: {len(selected_features)}",
                "\nПараметры модели:",
                str(settings),
                "\nМетрики качества:"
            ]

            if is_classification:
                accuracy = accuracy_score(y_test, y_pred)
                info.append(f"Точность: {accuracy:.4f}")
            else:
                mae = mean_absolute_error(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                info.extend([
                    f"Средняя абсолютная ошибка (MAE): {mae:.4f}",
                    f"Среднеквадратичная ошибка (MSE): {mse:.4f}",
                    f"Коэффициент детерминации (R²): {r2:.4f}"
                ])

            # Важность признаков (если поддерживается моделью)
            if hasattr(self.model, 'feature_importances_'):
                importances = pd.DataFrame({
                    'Признак': selected_features,
                    'Важность': self.model.feature_importances_
                }).sort_values('Важность', ascending=False)
                info.append("\nВажность признаков:")
                info.append(importances.to_string(index=False))
            elif hasattr(self.model, 'coef_'):
                coefs = pd.DataFrame({
                    'Признак': selected_features,
                    'Коэффициент': self.model.coef_[0] if is_classification else self.model.coef_
                }).sort_values('Коэффициент', key=abs, ascending=False)
                info.append("\nКоэффициенты модели:")
                info.append(coefs.to_string(index=False))

            self.model_info.setPlainText("\n".join(info))
            QMessageBox.information(self, "Успех", "Модель успешно обучена!")



        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обучения модели:\n{str(e)}")

    def make_prediction(self):
        """Прогнозирование на основе введенных значений"""
        if not hasattr(self, 'model'):
            QMessageBox.warning(self, "Ошибка", "Сначала обучите модель!")
            return

        try:
            # Собираем введенные значения только для выбранных признаков
            input_data = {}
            for feature, widgets in self.feature_widgets.items():
                if widgets['checkbox'].isChecked():
                    if isinstance(widgets['input'], QComboBox):
                        input_data[feature] = float(widgets['input'].currentText())
                    else:
                        input_data[feature] = widgets['input'].value()

            if not input_data:
                QMessageBox.warning(self, "Ошибка", "Нет выбранных признаков для прогноза!")
                return

            # Преобразуем в DataFrame с одной строкой
            X = pd.DataFrame([input_data])

            # Делаем прогноз
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
        """Обновление полей ввода с чекбоксами"""
        # Очистка предыдущих полей
        for i in reversed(range(self.input_layout.count())):
            widget = self.input_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        self.feature_widgets = {}

        if self.data is None or not self.target_combo.currentText():
            return

        target = self.target_combo.currentText()
        numeric_cols = self.data.select_dtypes(include=np.number).columns.tolist()
        features = [col for col in numeric_cols if col != target]

        # Настройки сетки - 4 колонки: чекбокс, название, значение
        COLS = 4
        row = col = 0

        for feature in features:
            # Чекбокс признака
            cb = QCheckBox()
            cb.setChecked(False)
            cb.stateChanged.connect(self.update_feature_state)

            # Название признака
            label = QLabel(feature)
            label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

            # Поле ввода
            if self.data[feature].nunique() < 10:
                widget = QComboBox()
                unique_vals = sorted(self.data[feature].unique())
                widget.addItems(map(str, unique_vals))
                widget.setFixedWidth(100)
                widget.setEnabled(False)
            else:
                widget = QDoubleSpinBox()
                widget.setRange(float(self.data[feature].min()),
                                float(self.data[feature].max()))
                widget.setValue(float(self.data[feature].median()))
                widget.setSingleStep(0.1)
                widget.setFixedWidth(100)
                widget.setEnabled(False)

            # Сохраняем виджеты
            self.feature_widgets[feature] = {
                'checkbox': cb,
                'label': label,
                'input': widget
            }

            # Добавляем в сетку
            self.input_layout.addWidget(cb, row, col * 3)
            self.input_layout.addWidget(label, row, col * 3 + 1)
            self.input_layout.addWidget(widget, row, col * 3 + 2)

            col += 1
            if col >= COLS:
                col = 0
                row += 1

        # Подключаем обработчик "Выбрать все"
        self.select_all_checkbox.stateChanged.connect(self.toggle_all_features)

    def toggle_all_features(self, state):
        """Обработчик чекбокса 'Выбрать все'"""
        # Блокируем сигналы чекбоксов, чтобы избежать рекурсии
        for feature, widgets in self.feature_widgets.items():
            widgets['checkbox'].blockSignals(True)

        # Устанавливаем состояние всех чекбоксов в соответствии с "Выбрать все"
        for feature, widgets in self.feature_widgets.items():
            widgets['checkbox'].setChecked(state)
            self.update_feature_widgets(feature, state)

        # Разблокируем сигналы чекбоксов
        for feature, widgets in self.feature_widgets.items():
            widgets['checkbox'].blockSignals(False)

    def update_feature_state(self):
        """Обновление состояния при изменении чекбокса признака"""
        # Проверяем, все ли чекбоксы выбраны
        all_checked = all(widgets['checkbox'].isChecked() for widgets in self.feature_widgets.values())

        # Блокируем сигнал чекбокса "Выбрать все" для избежания рекурсии
        self.select_all_checkbox.blockSignals(True)
        self.select_all_checkbox.setChecked(all_checked)
        self.select_all_checkbox.blockSignals(False)

        # Обновляем состояние конкретного признака
        for feature, widgets in self.feature_widgets.items():
            if widgets['checkbox'] == self.sender():
                self.update_feature_widgets(feature, widgets['checkbox'].isChecked())
                break
    def update_feature_widgets(self, feature, is_checked):
        """Обновление состояния виджетов конкретного признака"""
        widgets = self.feature_widgets[feature]
        widgets['input'].setEnabled(is_checked)

        # Визуальное выделение
        if is_checked:
            widgets['label'].setStyleSheet("color: black; font-weight: normal;")
        else:
            widgets['label'].setStyleSheet("color: gray; font-style: italic;")

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
        msg.exec()

    def show_about(self):
        """Информация о программе"""
        QMessageBox.about(self, "О программе",
                          "Анализатор биомедицинских данных v1.0\n"
                          "Для работы с клиническими показателями пациентов")


