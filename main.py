import sys
import pandas as pd
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QComboBox, QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QCheckBox, QFileDialog, QTableView, QTextEdit, QMessageBox, QDialog, QFormLayout, QInputDialog, QSizePolicy
)
from PySide6.QtCore import Qt, QAbstractTableModel, QSettings, QSize, Signal
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder


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
        colname = self._data.columns[column]
        self._data = self._data.sort_values(colname, ascending=order == Qt.AscendingOrder)
        self.layoutChanged.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data = None
        self.original_data = None  # Сохраняем оригинальные данные для сброса фильтров
        self.setWindowTitle("Анализ биомедицинских данных")
        self.setGeometry(100, 100, 1200, 700)
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
        self.btn_reset_filter = QPushButton("Сбросить фильтры")

        layout_actions.addWidget(QLabel("Путь к файлу:"))
        layout_actions.addWidget(self.file_path_edit)
        layout_actions.addWidget(self.btn_load)
        layout_actions.addWidget(self.btn_save)
        layout_actions.addWidget(self.btn_export)
        layout_actions.addWidget(self.btn_filter)
        layout_actions.addWidget(self.btn_reset_filter)
        left_layout.addWidget(group_actions)

        # Группа "Столбцы"
        group_columns = QGroupBox("Столбцы для анализа")
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
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout_tab_stats = QVBoxLayout(self.tab_stats)
        layout_tab_stats.addWidget(self.stats_text)

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
        self.btn_analyze = QPushButton("Выполнить анализ")

        layout_tab_analysis = QVBoxLayout(self.tab_analysis)
        layout_tab_analysis.addWidget(self.btn_analyze)
        layout_tab_analysis.addWidget(self.analysis_text)

        # Новая вкладка "Прогнозирование"
        self.tab_prediction = QWidget()
        self.prediction_text = QTextEdit()
        self.prediction_text.setReadOnly(True)

        self.feature_combo = QComboBox()
        self.target_combo = QComboBox()
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Линейная регрессия", "Случайный лес"])
        self.btn_train = QPushButton("Обучить модель")
        self.btn_predict = QPushButton("Сделать прогноз")

        form_layout = QFormLayout()
        form_layout.addRow("Признаки:", self.feature_combo)
        form_layout.addRow("Целевая переменная:", self.target_combo)
        form_layout.addRow("Модель:", self.model_combo)

        layout_tab_prediction = QVBoxLayout(self.tab_prediction)
        layout_tab_prediction.addLayout(form_layout)
        layout_tab_prediction.addWidget(self.btn_train)
        layout_tab_prediction.addWidget(self.btn_predict)
        layout_tab_prediction.addWidget(self.prediction_text)

        # Добавляем вкладки
        self.tabs.addTab(self.tab_data, "Данные")
        self.tabs.addTab(self.tab_stats, "Статистика")
        self.tabs.addTab(self.tab_visual, "Визуализация")
        self.tabs.addTab(self.tab_analysis, "Анализ")
        self.tabs.addTab(self.tab_prediction, "Прогнозирование")

        right_layout.addWidget(self.tabs)
        main_layout.addWidget(left_panel, stretch=1)
        main_layout.addWidget(right_panel, stretch=3)

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

    def load_data(self):
        """Загрузка данных из Excel файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл Excel", "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )

        if file_path:
            try:
                self.data = pd.read_excel(file_path)
                self.original_data = self.data.copy()  # Сохраняем оригинальные данные
                self.file_path_edit.setText(file_path)
                self.update_table_view()
                self.update_columns_list()
                self.show_stats()
                self.update_prediction_combos()
                QMessageBox.information(self, "Успех", "Данные успешно загружены!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки файла:\n{str(e)}")

    def update_prediction_combos(self):
        """Обновление комбобоксов для прогнозирования"""
        if self.data is not None:
            numeric_cols = self.data.select_dtypes(include=np.number).columns.tolist()
            self.feature_combo.clear()
            self.feature_combo.addItems(numeric_cols)
            self.target_combo.clear()
            self.target_combo.addItems(numeric_cols)

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

    def train_model(self):
        """Обучение модели машинного обучения"""
        if self.data is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите данные!")
            return

        try:
            features = [self.feature_combo.currentText()]
            target = self.target_combo.currentText()
            model_type = self.model_combo.currentText()

            # Подготовка данных
            X = self.data[features].values
            y = self.data[target].values

            # Разделение на обучающую и тестовую выборки
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Обучение модели
            if model_type == "Линейная регрессия":
                model = LinearRegression()
            else:  # "Случайный лес"
                model = RandomForestRegressor(n_estimators=100, random_state=42)

            model.fit(X_train, y_train)

            # Прогнозирование и оценка
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)

            # Сохраняем модель для последующего использования
            self.current_model = model
            self.current_features = features
            self.current_target = target

            # Вывод результатов
            report = [
                f"=== Результаты обучения модели ===",
                f"Тип модели: {model_type}",
                f"Признаки: {', '.join(features)}",
                f"Целевая переменная: {target}",
                f"Размер обучающей выборки: {len(X_train)}",
                f"Размер тестовой выборки: {len(X_test)}",
                f"Среднеквадратичная ошибка (MSE): {mse:.4f}",
                f"Коэффициент детерминации (R²): {r2:.4f}",
                "\nКоэффициенты модели:"
            ]

            if model_type == "Линейная регрессия":
                report.append(f"Пересечение (intercept): {model.intercept_:.4f}")
                for feature, coef in zip(features, model.coef_):
                    report.append(f"{feature}: {coef:.4f}")
            else:
                for feature, importance in zip(features, model.feature_importances_):
                    report.append(f"{feature}: {importance:.4f} (важность)")

            self.prediction_text.setPlainText("\n".join(report))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обучения модели:\n{str(e)}")

    def make_prediction(self):
        """Создание прогноза с использованием обученной модели"""
        if not hasattr(self, 'current_model'):
            QMessageBox.warning(self, "Ошибка", "Сначала обучите модель!")
            return

        try:
            # Получаем новое значение для прогноза
            value, ok = QInputDialog.getDouble(
                self, "Прогноз",
                f"Введите значение признака '{self.current_features[0]}' для прогноза:",
                decimals=4
            )

            if ok:
                # Создаем прогноз
                prediction = self.current_model.predict([[value]])

                # Показываем результат
                QMessageBox.information(
                    self, "Результат прогноза",
                    f"Прогнозируемое значение '{self.current_target}': {prediction[0]:.4f}\n"
                    f"При значении '{self.current_features[0]}' = {value}"
                )

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка создания прогноза:\n{str(e)}")

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
    def show_stats(self):
        """Отображение статистики данных"""
        if self.data is not None:
            stats = []
            stats.append("=== Основная статистика ===")
            stats.append(str(self.data.describe().round(3)))
            self.stats_text.setPlainText("\n".join(stats))

    def plot_data(self):
        """Построение графиков"""
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
                # Фильтруем только числовые столбцы
                numeric_cols = [col for col in selected_cols
                                if pd.api.types.is_numeric_dtype(self.data[col])]

                if not numeric_cols:
                    QMessageBox.warning(self, "Ошибка", "Выберите числовые столбцы для гистограммы!")
                    return

                # Настройки гистограммы
                bins = min(20, len(self.data) // 5)
                alpha = 0.7

                # Строим гистограмму и получаем данные столбцов
                n, bins, patches = ax.hist(
                    [self.data[col] for col in numeric_cols],
                    bins=bins,
                    alpha=alpha,
                    label=numeric_cols
                )

                # Добавляем подписи значений на каждый столбец
                for i in range(len(patches)):
                    for j in range(len(patches[i])):
                        height = patches[i][j].get_height()
                        if height > 0:  # Подписываем только непустые столбцы
                            ax.text(
                                patches[i][j].get_x() + patches[i][j].get_width() / 2.,
                                height,
                                f'{int(height)}',
                                ha='center',
                                va='bottom',
                                fontsize=8
                            )

                # Настраиваем заголовки и легенду
                ax.set_title("Гистограммы распределения", pad=15, fontsize=12)
                ax.set_xlabel("Значения", fontsize=10)
                ax.set_ylabel("Частота", fontsize=10)
                ax.legend(loc='upper right')

                # Добавляем сетку
                ax.grid(True, linestyle='--', alpha=0.5)

                # Автонастройка отступов
                self.figure.tight_layout()

            elif plot_type == "Боксплот":
                numeric_cols = [col for col in selected_cols
                                if pd.api.types.is_numeric_dtype(self.data[col])]
                if numeric_cols:
                    self.data[numeric_cols].plot.box(ax=ax)
                    ax.set_title("Боксплоты распределения")
                else:
                    QMessageBox.warning(self, "Ошибка", "Выберите числовые столбцы!")
                    return

            elif plot_type == "Точечный график":
                if len(selected_cols) >= 2:
                    x_col = selected_cols[0]
                    y_col = selected_cols[1]
                    if (pd.api.types.is_numeric_dtype(self.data[x_col]) and
                            pd.api.types.is_numeric_dtype(self.data[y_col])):
                        self.data.plot.scatter(x=x_col, y=y_col, ax=ax)
                        ax.set_title(f"{x_col} vs {y_col}")
                    else:
                        QMessageBox.warning(self, "Ошибка", "Выберите числовые столбцы!")
                else:
                    QMessageBox.warning(self, "Ошибка", "Выберите 2 столбца!")

            elif plot_type == "Линейный график":
                for col in selected_cols:
                    if pd.api.types.is_numeric_dtype(self.data[col]):
                        self.data[col].plot(ax=ax)
                ax.set_title("Линейные графики")
                ax.legend(selected_cols)

            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка построения графика:\n{str(e)}")

    def run_analysis(self):
        """Выполнение базового анализа данных с тепловой картой корреляции"""
        if self.data is None:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите данные!")
            return

        analysis_report = []
        analysis_report.append("=== Базовый анализ биомедицинских данных ===")

        # Анализ корреляций
        numeric_cols = self.data.select_dtypes(include=np.number).columns
        if len(numeric_cols) > 1:
            corr_matrix = self.data[numeric_cols].corr()
            analysis_report.append("\n=== Корреляционная матрица ===")
            analysis_report.append(str(corr_matrix.round(2)))

            # Находим сильные корреляции
            strong_corr = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i + 1, len(corr_matrix.columns)):
                    if abs(corr_matrix.iloc[i, j]) > 0.7:
                        strong_corr.append(
                            f"{corr_matrix.columns[i]} и {corr_matrix.columns[j]}: {corr_matrix.iloc[i, j]:.2f}"
                        )
            if strong_corr:
                analysis_report.append("\n=== Сильные корреляции (|r| > 0.7) ===")
                analysis_report.extend(strong_corr)

            # Создаем отдельное окно для тепловой карты
            self.show_correlation_heatmap(corr_matrix)

        # Анализ категориальных данных
        cat_cols = self.data.select_dtypes(exclude=np.number).columns
        if len(cat_cols) > 0:
            analysis_report.append("\n=== Частоты категориальных переменных ===")
            for col in cat_cols:
                analysis_report.append(f"\n{col}:")
                analysis_report.append(str(self.data[col].value_counts()))

        self.analysis_text.setPlainText("\n".join(analysis_report))

    def show_correlation_heatmap(self, corr_matrix):
        """Отображает тепловую карту корреляционной матрицы в отдельном окне (на весь экран)"""
        # Создаем новое окно
        heatmap_window = QDialog(self)
        heatmap_window.setWindowTitle("Тепловая карта корреляции")
        heatmap_window.setWindowState(Qt.WindowMaximized)  # Разворачиваем на весь экран

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Убираем отступы

        # Создаем фигуру и холст
        figure = Figure()
        canvas = FigureCanvas(figure)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Растягиваем на все доступное пространство
        toolbar = NavigationToolbar(canvas, heatmap_window)

        # Настраиваем тепловую карту
        ax = figure.add_subplot(111)
        sns.heatmap(
            corr_matrix,
            ax=ax,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            center=0,
            linewidths=0.5,
            annot_kws={"size": 10}  # Увеличиваем размер аннотаций
        )

        # Настраиваем подписи
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

        # Увеличиваем заголовок
        ax.set_title("Тепловая карта корреляционной матрицы", pad=20, fontsize=12)

        # Автоматически подгоняем макет
        figure.tight_layout()

        # Добавляем элементы в layout
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())