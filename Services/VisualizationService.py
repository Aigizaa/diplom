import pandas as pd
import numpy as np


class VisualizationService:
    def __init__(self, data=None, parent_ui=None):
        self.data = data  # pandas.DataFrame
        self.parent_ui = parent_ui  # Ссылка на главное окно для вызова диалогов
        self.figure = parent_ui.figure
        self.canvas = None

    def set_canvas(self, canvas):
        """Установить canvas для отрисовки графиков"""
        self.canvas = canvas

    def plot_data(self, selected_cols, plot_type):
        if plot_type == "Гистограмма":
            self._plot_histogram(selected_cols)
        elif plot_type == "Диаграмма рассеяния по осям":
            self._plot_scatter_by_axis(selected_cols)
        elif plot_type == "Точечный график":
            self._plot_scatter(selected_cols)
        elif plot_type == "Линейный график":
            self._plot_line(selected_cols)
        elif plot_type == "Круговая диаграмма":
            self._plot_pie(selected_cols)

        self.figure.tight_layout()
        if self.canvas:
            self.canvas.draw()

    def _plot_histogram(self, selected_cols):
        """Построение гистограмм"""
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
                raise ValueError("Нет подходящих данных для гистограммы")

    def _plot_scatter_by_axis(self, selected_cols):
        """Диаграмма рассеяния по осям"""
        num_cols = [col for col in selected_cols if pd.api.types.is_numeric_dtype(self.data[col])]
        if not num_cols:
            raise ValueError("Диаграмма требует числовых данных")

        for idx, col in enumerate(num_cols):
            ax = self.figure.add_subplot(1, len(num_cols), idx + 1)
            ax.plot(self.data[col], 'o', markersize=4)
            ax.set_title(col)
            ax.set_xlabel("Индекс")
            ax.set_ylabel(col)

    def _plot_scatter(self, selected_cols):
        """Точечный график"""
        num_cols = [col for col in selected_cols if pd.api.types.is_numeric_dtype(self.data[col])]
        if len(num_cols) < 2:
            raise ValueError("Нужно выбрать 2 числовых столбца")

        ax = self.figure.add_subplot(111)
        x, y = num_cols[0], num_cols[1]
        self.data.plot.scatter(x=x, y=y, ax=ax)
        ax.set_title(f"{x} vs {y}")

    def _plot_line(self, selected_cols):
        """Линейный график"""
        num_cols = [col for col in selected_cols if pd.api.types.is_numeric_dtype(self.data[col])]
        if not num_cols:
            raise ValueError("Нет числовых данных для построения")

        ax = self.figure.add_subplot(111)
        self.data[num_cols].plot(ax=ax)
        ax.set_title("Линейные графики")

    def _plot_pie(self, selected_cols):
        """Круговая диаграмма"""
        n = len(selected_cols)
        if n == 0:
            raise ValueError("Выберите хотя бы один столбец")

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
