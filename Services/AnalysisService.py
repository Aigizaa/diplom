import pandas as pd
import numpy as np


class AnalysisService:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def get_correlation_analysis_report(self):

        # Выбираем только числовые колонки
        numeric_cols = self.data.select_dtypes(include=np.number).columns
        if len(numeric_cols) < 2:
            raise ValueError("Недостаточно числовых данных для анализа корреляций")

        corr_matrix = self.get_correlation_matrix()

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

        return report

    def get_correlation_matrix(self):
        # Выбираем только числовые колонки
        numeric_cols = self.data.select_dtypes(include=np.number).columns
        if len(numeric_cols) < 2:
            raise ValueError("Недостаточно числовых данных для анализа корреляций")
        # Считаем корреляционную матрицу
        corr_matrix = self.data[numeric_cols].corr()
        return corr_matrix



