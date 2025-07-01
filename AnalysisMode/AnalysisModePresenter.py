import os
import pandas as pd
import numpy as np
from PySide6.QtGui import QFont

from Services.StatisticsService import StatisticsService
from Services.ForcastingService import ForcastingService
from Services.VisualizationService import VisualizationService
from Services.AnalysisService import AnalysisService
from Services.CloudService import GoogleDriveService
from AnalysisMode.AnalysisModeView import AnalysisModeView
from PySide6.QtWidgets import (
    QVBoxLayout,
    QComboBox, QLabel, QPushButton, QListWidgetItem,
    QCheckBox, QFileDialog, QMessageBox, QDialog,
    QDoubleSpinBox, QSizePolicy, QListWidget, QHBoxLayout
)
import seaborn as sns
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSpinBox, QDialogButtonBox
from PandasModel import PandasModel
from FilterDialog import FilterDialog
from ModelSettingsDialog import ModelSettingsData, ModelSettingsView, ModelSettingsPresenter


class ClusterDialog(QDialog):
    def __init__(self, features, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки кластерного анализа")
        self.layout = QVBoxLayout(self)

        # Выбор признаков
        self.features_list = QListWidget()
        self.features_list.setSelectionMode(QListWidget.MultiSelection)
        self.features_list.addItems(features)
        self.layout.addWidget(QLabel("Выберите признаки для кластеризации:"))
        self.layout.addWidget(self.features_list)

        # Количество кластеров
        self.cluster_spin = QSpinBox()
        self.cluster_spin.setRange(2, 10)
        self.cluster_spin.setValue(3)
        cluster_layout = QHBoxLayout()
        cluster_layout.addWidget(QLabel("Количество кластеров:"))
        cluster_layout.addWidget(self.cluster_spin)
        self.layout.addLayout(cluster_layout)

        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.layout.addWidget(button_box)

    def get_selected_features(self):
        return [item.text() for item in self.features_list.selectedItems()]

    def get_cluster_count(self):
        return self.cluster_spin.value()


class AnalysisModePresenter:
    def __init__(self, view: AnalysisModeView):
        self.view = view
        self.data = None
        self.original_data = None
        self.model = None
        self.connect_signals()
        self.update_model_combo(self.view.task_type_combo.currentText())
        self.model_settings_data = ModelSettingsData()

    def connect_signals(self):
        """Подключение сигналов к слотам"""
        self.view.btn_load_local.clicked.connect(self.load_local_data)
        self.view.btn_save_local.clicked.connect(self.save_local_data)
        self.view.btn_load_from_cloud.clicked.connect(self.load_data_from_cloud)
        self.view.btn_save_to_cloud.clicked.connect(self.save_data_to_cloud)

        self.view.btn_filter.clicked.connect(self.apply_filter)
        self.view.btn_reset_filter.clicked.connect(self.reset_filter)

        self.view.btn_refresh_stats.clicked.connect(self.show_stats)
        self.view.btn_save_stats.clicked.connect(self.save_stats)

        self.view.btn_export.clicked.connect(self.export_plots)
        self.view.btn_plot.clicked.connect(self.plot_data)

        self.view.btn_train.clicked.connect(self.train_model)
        self.view.btn_predict.clicked.connect(self.make_prediction)
        self.view.target_combo.currentTextChanged.connect(self.on_target_changed)
        self.view.task_type_combo.currentTextChanged.connect(self.update_model_combo)
        self.view.btn_model_settings.clicked.connect(self.show_model_settings)

        self.view.about_action.triggered.connect(self.show_about)
        self.view.create_action.triggered.connect(self.open_editing_mode)
        self.view.legend_action.triggered.connect(self.show_legend)
        self.setup_analysis_connections()

    def load_local_data(self):
        """Загрузка данных из файла (Excel или CSV) с обновлением интерфейса"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.view, "Открыть файл данных",
            "", "Excel Files (*.xlsx *.xls);;CSV Files (*.csv)"
        )
        if not file_path:
            return  # Пользователь отменил выбор файла

        try:
            # Проверка размера файла перед чтением
            if os.path.getsize(file_path) == 0:
                raise ValueError("Выбранный файл пустой!")

            if file_path.lower().endswith(('.xlsx', '.xls')):
                # Чтение Excel файла
                self.data = pd.read_excel(file_path)
                # Дополнительная проверка для Excel
                if self.data.empty:
                    raise ValueError("Файл Excel не содержит данных")
            elif file_path.lower().endswith('.csv'):
                # Чтение CSV файла с автоматическим определением разделителя
                self.data = pd.read_csv(file_path, encoding='utf-8-sig')
                # Проверка для CSV (могли прочитать только заголовки)
                if self.data.empty or len(self.data.columns) == 0:
                    raise ValueError("CSV файл не содержит данных")
            else:
                raise ValueError("Неподдерживаемый формат файла")

            self.original_data = self.data.copy()
            self.view.file_path_edit.setText(file_path)

            # Инициализация таблицы данных
            model = PandasModel(self.data)
            self.view.table_view.setModel(model)
            self.view.table_view.setSortingEnabled(True)
            self.view.table_view.resizeColumnsToContents()

            # Обновление интерфейса
            self.update_columns_list()
            self.show_stats()
            self.update_prediction_combos()

            QMessageBox.information(self.view, "Успех", f"Данные успешно загружены!\nЗагружено строк: {len(self.data)}")

        except ValueError as e:
            if "пустой" in str(e).lower():
                QMessageBox.critical(self.view, "Ошибка", "Ошибка: Файл пустой")
            else:
                QMessageBox.critical(self.view, "Ошибка", f"Ошибка загрузки файла:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self.view, "Ошибка", f"Ошибка загрузки файла:\n{str(e)}")

    def save_local_data(self):
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

    def load_data_from_cloud(self):
        """Загружает данные из Google Диска."""
        cloud_service = GoogleDriveService(parent_ui=self.view)
        self.data, file, error = cloud_service.load_from_cloud()

        if error:
            QMessageBox.critical(self.view, "Ошибка", error)
        else:
            # Инициализация таблицы данных
            self.model = PandasModel(self.data)
            self.view.table_view.setModel(self.model)
            self.view.table_view.setSortingEnabled(True)
            self.view.table_view.resizeColumnsToContents()

            # Обновление интерфейса
            self.update_columns_list()
            self.show_stats()
            self.update_prediction_combos()
            self.view.file_path_edit.setText(file['name'])
            QMessageBox.information(self.view, "Успех", "Данные успешно загружены!")

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

    def apply_filter(self):
        """Применение фильтра к данным"""
        if self.data is None:
            QMessageBox.warning(self.view, "Ошибка", "Сначала загрузите данные!")
            return

        dialog = FilterDialog(self.data.columns.tolist(), self.view)
        if dialog.exec():
            filter_params = dialog.get_filter()
            try:
                column = filter_params['column']
                operator = filter_params['operator']
                value = filter_params['value']

                # Сохраняем исходные данные для восстановления при пустом результате
                filtered_data = self.data.copy()

                if operator == "содержит":
                    filtered_data = filtered_data[filtered_data[column].astype(str).str.contains(value, case=False)]
                else:
                    # Пробуем преобразовать значение в число
                    try:
                        value = float(value) if '.' in value else int(value)
                    except ValueError:
                        pass  # Оставляем как строку, если не число

                    if operator == ">":
                        filtered_data = filtered_data[filtered_data[column] > value]
                    elif operator == ">=":
                        filtered_data = filtered_data[filtered_data[column] >= value]
                    elif operator == "==":
                        filtered_data = filtered_data[filtered_data[column] == value]
                    elif operator == "<=":
                        filtered_data = filtered_data[filtered_data[column] <= value]
                    elif operator == "<":
                        filtered_data = filtered_data[filtered_data[column] < value]
                    elif operator == "!=":
                        filtered_data = filtered_data[filtered_data[column] != value]

                # Проверка на пустой результат
                if filtered_data.empty:
                    QMessageBox.warning(self.view, "Ошибка", "Не найдено данных, удовлетворяющих условию")
                    return

                # Применяем фильтр только если есть результаты
                self.data = filtered_data
                self.update_table_view()
                QMessageBox.information(self.view, "Успех",
                                        f"Найдено строк: {len(self.data)}\nФильтр успешно применен!")

            except Exception as e:
                QMessageBox.critical(self.view, "Ошибка", f"Ошибка применения фильтра:\n{str(e)}")

    def reset_filter(self):
        """Сброс фильтров и восстановление оригинальных данных"""
        if self.original_data is not None:
            self.data = self.original_data.copy()
            self.update_table_view()
            self.show_stats()
            QMessageBox.information(self.view, "Успех", "Фильтры сброшены!")

    def update_table_view(self):
        """Обновление табличного представления данных"""
        if self.data is not None:
            model = PandasModel(self.data)
            self.view.table_view.setModel(model)
            self.view.table_view.resizeColumnsToContents()

    def update_columns_list(self):
        """Обновление списка столбцов"""
        self.view.columns_list.clear()
        if self.data is not None:
            for col in self.data.columns:
                item = QListWidgetItem(col)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Unchecked)
                self.view.columns_list.addItem(item)

    def show_stats(self):
        """Отображение статистики данных в таблице на вкладке Статистика"""
        if self.data is None:
            QMessageBox.warning(self.view, "Ошибка", "Сначала загрузите данные!")
            return
        try:
            statistics = StatisticsService(self.data, self.view)
            stats_df = statistics.get_statistics()
            # Создаем модель для таблицы
            model = PandasModel(stats_df)
            self.view.stats_table.setModel(model)
            self.view.stats_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self.view, "Ошибка", f"Ошибка при расчете статистики:\n{str(e)}")

    def save_stats(self):
        """Сохранение статистики в файл"""
        if self.data is None:
            QMessageBox.warning(self.view, "Ошибка", "Нет данных для сохранения статистики!")
            return
        try:
            statistics = StatisticsService(self.data, self.view)
            stats_df = statistics.get_statistics()
            # Диалог сохранения файла
            file_path, _ = QFileDialog.getSaveFileName(
                self.view,
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
                    stats_df.to_excel(file_path)
                QMessageBox.information(self.view, "Успех", "Статистика успешно сохранена!")

        except Exception as e:
            QMessageBox.critical(self.view, "Ошибка", f"Ошибка сохранения статистики:\n{str(e)}")

    def plot_data(self):
        if self.data is None:
            QMessageBox.warning(self.view, "Ошибка", "Сначала загрузите данные!")
            return

        selected_cols = []
        for i in range(self.view.columns_list.count()):
            if self.view.columns_list.item(i).checkState() == Qt.CheckState.Checked:
                selected_cols.append(self.view.columns_list.item(i).text())

        if not selected_cols:
            QMessageBox.warning(self.view, "Ошибка", "Выберите хотя бы один столбец!")
            return

        plot_type = self.view.plot_type_combo.currentText()
        self.view.figure.clear()

        try:
            visualization = VisualizationService(self.data, self.view)
            visualization.set_canvas(self.view.canvas)  # Передаем canvas для отрисовки
            visualization.plot_data(selected_cols, plot_type)

        except Exception as e:
            QMessageBox.critical(self.view, "Ошибка", f"Ошибка построения графика:\n{str(e)}")

    def export_plots(self):
        """Экспорт графиков в файл"""
        if self.data is None:
            QMessageBox.warning(self.view, "Ошибка", "Нет данных для экспорта!")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self.view, "Экспорт графиков", "",
            "PNG Files (*.png);;PDF Files (*.pdf)"
        )
        if file_path:
            try:
                self.view.figure.savefig(file_path)
                QMessageBox.information(self.view, "Успех", "График успешно экспортирован!")
            except Exception as e:
                QMessageBox.critical(self.view, "Ошибка", f"Ошибка экспорта:\n{str(e)}")

    def setup_analysis_connections(self):
        """Подключение сигналов для новых видов анализа"""
        self.view.btn_correlation.clicked.connect(self.run_correlation_analysis)
        self.view.btn_distribution.clicked.connect(self.run_distribution_analysis)
        self.view.btn_outliers.clicked.connect(self.run_outliers_analysis)
        self.view.btn_missing.clicked.connect(self.run_missing_data_analysis)
        self.view.btn_cluster.clicked.connect(self.run_cluster_analysis)

    def run_correlation_analysis(self):
        """Анализ корреляций (существующий метод)"""
        if self.data is None:
            QMessageBox.warning(self.view, "Ошибка", "Сначала загрузите данные!")
            return
        try:
            analysis = AnalysisService(self.data)
            report = analysis.get_correlation_analysis_report()
            self.view.analysis_text.setPlainText("\n".join(report))
            # Показываем тепловую карту
            corr_matrix = analysis.get_correlation_matrix()
            self.show_correlation_heatmap(corr_matrix)
        except Exception as e:
            QMessageBox.critical(self.view, "Ошибка", f"Ошибка анализа данных:\n{str(e)}")

    def run_distribution_analysis(self):
        """Анализ распределений данных"""
        if self.data is None:
            QMessageBox.warning(self.view, "Ошибка", "Сначала загрузите данные!")
            return

        try:
            analysis = AnalysisService(self.data)
            report = analysis.get_distribution_analysis_report()

            font = QFont("Courier New", 10)
            self.view.analysis_text.setFont(font)
            self.view.analysis_text.setPlainText("\n".join(report))

            QMessageBox.information(self.view, "Успех", "Анализ распределений выполнен!")
        except Exception as e:
            QMessageBox.critical(self.view, "Ошибка", f"Ошибка анализа распределений:\n{str(e)}")

    def run_outliers_analysis(self):
        """Анализ выбросов в данных"""
        if self.data is None:
            QMessageBox.warning(self.view, "Ошибка", "Сначала загрузите данные!")
            return

        try:
            analysis = AnalysisService(self.data)
            report, outliers_count = analysis.get_outliers_analysis_report()

            self.view.analysis_text.setPlainText("\n".join(report))
            font = QFont("Courier New", 10)
            self.view.analysis_text.setFont(font)
            self.view.analysis_text.setPlainText("\n".join(report))
            QMessageBox.information(self.view, "Успех", "Анализ выбросов выполнен!")
        except Exception as e:
            QMessageBox.critical(self.view, "Ошибка", f"Ошибка анализа выбросов:\n{str(e)}")

    def run_missing_data_analysis(self):
        """Анализ пропущенных значений"""
        if self.data is None:
            QMessageBox.warning(self.view, "Ошибка", "Сначала загрузите данные!")
            return

        try:
            analysis = AnalysisService(self.data)
            report = analysis.get_missing_data_analysis_report()

            # Визуализация пропусков
            self.view.figure.clear()
            ax = self.view.figure.add_subplot(111)

            missing = self.data.isnull().sum()
            missing = missing[missing > 0]
            if not missing.empty:
                missing.plot(kind='bar', ax=ax)
                ax.set_title("Количество пропущенных значений")
                ax.set_ylabel("Количество пропусков")
                self.view.canvas.draw()

            self.view.analysis_text.setPlainText("\n".join(report))
            QMessageBox.information(self.view, "Успех", "Анализ пропусков выполнен!")
        except Exception as e:
            QMessageBox.critical(self.view, "Ошибка", f"Ошибка анализа пропусков:\n{str(e)}")

    def run_cluster_analysis(self):
        """Кластерный анализ данных"""
        if self.data is None:
            QMessageBox.warning(self.view, "Ошибка", "Сначала загрузите данные!")
            return

        try:
            numeric_cols = self.data.select_dtypes(include=np.number).columns.tolist()
            if len(numeric_cols) < 2:
                QMessageBox.warning(self.view, "Ошибка", "Недостаточно числовых признаков для кластеризации!")
                return

            # Диалог выбора признаков для кластеризации
            dialog = ClusterDialog(numeric_cols, self.view)
            if dialog.exec():
                features = dialog.get_selected_features()
                n_clusters = dialog.get_cluster_count()

                if len(features) < 2:
                    QMessageBox.warning(self.view, "Ошибка", "Выберите хотя бы 2 признака!")
                    return

                analysis = AnalysisService(self.data)
                report, cluster_labels = analysis.get_cluster_analysis_report(features, n_clusters)

                # Визуализация кластеров
                self.view.figure.clear()

                # размер графика (ширина x высота в дюймах)
                self.view.figure.set_size_inches(8, 6)

                ax = self.view.figure.add_subplot(111)

                # отступы вокруг графика
                self.view.figure.tight_layout(pad=2.0)

                if len(features) == 2:
                    sns.scatterplot(
                        x=self.data[features[0]],
                        y=self.data[features[1]],
                        hue=cluster_labels,
                        palette='viridis',
                        ax=ax,
                        s=40,  # Размер точек
                        alpha=0.7  # Прозрачность
                    )
                    ax.set_title("2D визуализация кластеров", fontsize=10)
                else:
                    # Для более чем 2 признаков используем PCA
                    from sklearn.decomposition import PCA
                    pca = PCA(n_components=2)
                    reduced = pca.fit_transform(self.data[features])
                    reduced_df = pd.DataFrame(reduced, columns=['PC1', 'PC2'])
                    sns.scatterplot(
                        x=reduced_df['PC1'],
                        y=reduced_df['PC2'],
                        hue=cluster_labels,
                        palette='viridis',
                        ax=ax,
                        s=40,
                        alpha=0.7
                    )
                    ax.set_title("PCA визуализация кластеров (2 главных компоненты)", fontsize=10)

                # Уменьшаем размер шрифта подписей
                ax.tick_params(axis='both', which='major', labelsize=8)
                ax.xaxis.label.set_size(8)
                ax.yaxis.label.set_size(8)

                # Компактное расположение легенды
                ax.legend(fontsize=8, bbox_to_anchor=(1.05, 1), loc='upper left')

                self.view.canvas.draw()
                self.view.analysis_text.setPlainText("\n".join(report))
                QMessageBox.information(self.view, "Успех", "Кластерный анализ выполнен!")
        except Exception as e:
            QMessageBox.critical(self.view, "Ошибка", f"Ошибка кластерного анализа:\n{str(e)}")

    def show_correlation_heatmap(self, corr_matrix):
        """Отображает тепловую карту корреляционной матрицы с полными подписями"""
        # Создаем новое окно
        heatmap_window = QDialog(self.view)
        heatmap_window.setWindowTitle("Тепловая карта корреляции")
        heatmap_window.setWindowState(Qt.WindowState.WindowMaximized)  # Разворачиваем на весь экран

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
            self.view,
            "Сохранить тепловую карту",
            "",
            "PNG Files (*.png);;JPEG Files (*.jpg);;PDF Files (*.pdf)"
        )
        if file_path:
            try:
                figure.savefig(file_path, bbox_inches='tight', dpi=300)
                QMessageBox.information(self.view, "Успех", "Тепловая карта успешно сохранена!")
            except Exception as e:
                QMessageBox.critical(self.view, "Ошибка", f"Ошибка сохранения:\n{str(e)}")

    def train_model(self):
        """Модифицированный метод обучения модели"""
        if self.data is None:
            QMessageBox.warning(self.view, "Ошибка", "Сначала загрузите данные!")
            return

        target = self.view.target_combo.currentText()
        if not target:
            return
        try:
            # Получаем только выбранные признаки
            selected_features = [feature for feature, widgets in self.feature_widgets.items()
                                 if widgets['checkbox'].isChecked()]
            if not selected_features:
                QMessageBox.warning(self.view, "Ошибка", "Выберите хотя бы один признак!")
                return

            # Определяем, регрессия или классификация
            task_type = self.view.task_type_combo.currentText()
            # Получаем тип модели и ее настройки
            model_type = self.view.model_combo.currentText()
            settings = self.get_current_model_settings()
            self.predictor = ForcastingService(self.data, selected_features, target)
            self.predictor.create_model(task_type, model_type, settings)
            self.predictor.train_model()

            # Активируем кнопку прогноза
            self.view.btn_predict.setEnabled(True)

            # Формируем информацию о модели
            info = [
                f"Модель: {model_type}",
                f"Тип: {task_type}",
                f"Целевой признак: {target}",
                f"Использовано признаков: {len(selected_features)}",
                "\nПараметры модели:",
                str(settings),
                "\nМетрики качества:"
            ]

            metrics = self.predictor.evaluate_model()
            metrics_str = "\n".join([f"{key}: {value}" for key, value in metrics.items()])
            info.append(metrics_str)

            model_info = self.predictor.get_info()
            info.append("\nПризнаки:")
            info.append(model_info)
            self.view.model_info.setPlainText("\n".join(info))
            QMessageBox.information(self.view, "Успех", "Модель успешно обучена!")

        except Exception as e:
            QMessageBox.critical(self.view, "Ошибка", f"Ошибка обучения модели:\n{str(e)}")

    def show_model_settings(self):
        """Показывает диалог настроек модели"""
        model_type = self.view.model_combo.currentText()
        view = ModelSettingsView(model_type, self.view)
        presenter = ModelSettingsPresenter(view, self.model_settings_data)
        if view.exec() == QDialog.accepted:
            print("Настройки сохранены")

    def get_current_model_settings(self):
        """Возвращает настройки текущей модели"""
        model_type = self.view.model_combo.currentText()
        return self.model_settings_data.get_settings(model_type)

    def make_prediction(self):
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
                QMessageBox.warning(self.view, "Ошибка", "Нет выбранных признаков для прогноза!")
                return

            # Преобразуем в DataFrame с одной строкой
            X = pd.DataFrame([input_data])
            # Делаем прогноз
            prediction = self.predictor.make_prediction(X)

            target = self.view.target_combo.currentText()
            self.view.prediction_result.setText(
                f"Прогнозируемое значение {target}: {prediction:.4f}"
            )
        except Exception as e:
            QMessageBox.critical(self.view, "Ошибка", f"Ошибка прогнозирования:\n{str(e)}")

    def on_target_changed(self):
        """Обработчик изменения целевой переменной"""
        if hasattr(self, 'data') and self.data is not None:
            self.update_input_fields()
            self.view.select_all_checkbox.setChecked(False)

    def update_model_combo(self, task_type):
        """Обновляет список моделей в зависимости от выбранного типа задачи"""
        self.view.model_combo.clear()  # Очищаем комбобокс
        if task_type == "Классификация":
            models = [
                "Случайный лес",
                "Логистическая регрессия",
                "K-ближайших соседей (KNN)",
                "Дерево решений",
                "Градиентный бустинг"
            ]
        elif task_type == "Прогнозирование":
            models = [
                "Случайный лес",
                "Линейная регрессия",
                "K-ближайших соседей (KNN)",
                "Дерево решений",
                "Градиентный бустинг"
            ]
        else:
            models = []
        self.view.model_combo.addItems(models)

    def open_editing_mode(self):
        from EditingMode.EditingModeView import EditingModeView
        from EditingMode.EditingModePresenter import EditingModePresenter
        from EditingMode.OsteoartritModel import OsteoartritModel
        self.creation_window = EditingModeView(self.view.current_user)
        self.model = OsteoartritModel()
        self.creation_presenter = EditingModePresenter(self.creation_window, self.model)
        self.creation_window.show()
        self.view.close()

    def show_about(self):
        """Информация о программе"""
        QMessageBox.about(self.view, "О программе",
                          "Анализатор биомедицинских данных v1.0\n"
                          "Для работы с клиническими показателями пациентов")

    @staticmethod
    def show_legend():
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
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.exec()

    def update_prediction_combos(self):
        """Обновление списка доступных признаков"""
        if self.data is None:
            return

        # Блокируем сигналы во избежание рекурсии
        self.view.target_combo.blockSignals(True)

        current_target = self.view.target_combo.currentText()
        self.view.target_combo.clear()

        numeric_cols = self.data.select_dtypes(include=np.number).columns.tolist()
        self.view.target_combo.addItems(numeric_cols)

        if current_target in numeric_cols:
            self.view.target_combo.setCurrentText(current_target)

        self.view.btn_train.setEnabled(len(numeric_cols) > 0)
        self.view.btn_predict.setEnabled(True)
        self.view.target_combo.blockSignals(False)
        self.update_input_fields()

    def update_input_fields(self):
        """Обновление полей ввода с чекбоксами"""
        # Очистка предыдущих полей
        for i in reversed(range(self.view.input_layout.count())):
            widget = self.view.input_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        self.feature_widgets = {}

        if self.data is None or not self.view.target_combo.currentText():
            return

        target = self.view.target_combo.currentText()
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
            label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)

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
            self.view.input_layout.addWidget(cb, row, col * 3)
            self.view.input_layout.addWidget(label, row, col * 3 + 1)
            self.view.input_layout.addWidget(widget, row, col * 3 + 2)

            col += 1
            if col >= COLS:
                col = 0
                row += 1

        # Подключаем обработчик "Выбрать все"
        self.view.select_all_checkbox.stateChanged.connect(self.toggle_all_features)

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
        self.view.select_all_checkbox.blockSignals(True)
        self.view.select_all_checkbox.setChecked(all_checked)
        self.view.select_all_checkbox.blockSignals(False)

        # Обновляем состояние конкретного признака
        for feature, widgets in self.feature_widgets.items():
            if widgets['checkbox'] == self.view.sender():
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
