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

    def get_distribution_analysis_report(self):
        """Анализ распределений данных с табличным форматированием"""
        numeric_cols = self.data.select_dtypes(include=np.number).columns
        report = []

        # Рассчитываем максимальные ширины столбцов
        max_name_len = max(len(str(col)) for col in numeric_cols) if not numeric_cols.empty else 15
        max_name_len = max(max_name_len, len("Признак"))

        # Шапка таблицы
        report.append("=" * (max_name_len + 72))
        report.append(f"{'АНАЛИЗ РАСПРЕДЕЛЕНИЙ ДАННЫХ':^{max_name_len + 72}}")
        report.append("=" * (max_name_len + 72))
        report.append("")

        # Формат строки с динамической шириной первого столбца
        row_format = (
            f"{{:<{max_name_len}}} | "
            f"{{:>10}} | "
            f"{{:>10}} | "
            f"{{:>18}} | "
            f"{{:>15}} | "
            f"{{:>12}}"
        )

        # Заголовки столбцов
        report.append(row_format.format(
            "Признак", "Среднее", "Медиана", "Скошенность", "Тип распределения", "Эксцесс"
        ))
        report.append("-" * (max_name_len + 72))

        # Данные
        for col in numeric_cols:
            mean = self.data[col].mean()
            median = self.data[col].median()
            skewness = self.data[col].skew()
            kurtosis = self.data[col].kurtosis()

            dist_type = "нормальное" if -0.5 < skewness < 0.5 else (
                "скошенное вправо" if skewness > 0 else "скошенное влево"
            )

            report.append(row_format.format(
                col,
                f"{mean:.2f}",
                f"{median:.2f}",
                f"{skewness:.2f}",
                dist_type,
                f"{kurtosis:.2f}"
            ))

        # Пояснения
        report.append("\nПРИМЕЧАНИЯ:")
        report.append("- Скошенность: мера асимметрии распределения")
        report.append("  • 0 = симметричное (нормальное)")
        report.append("  • >0 = хвост справа (скошенное вправо)")
        report.append("  • <0 = хвост слева (скошенное влево)")
        report.append("- Эксцесс: мера остроты пика распределения")
        report.append("  • 0 = как нормальное распределение")
        report.append("  • >0 = более острый пик")
        report.append("  • <0 = более плоский пик")
        report.append(f"- Всего проанализировано признаков: {len(numeric_cols)}")

        return report

    def get_outliers_analysis_report(self):
        """Анализ выбросов по методу IQR"""
        report = ["=== Анализ выбросов (метод IQR) ==="]
        numeric_cols = self.data.select_dtypes(include=np.number).columns
        outliers_count = {}

        # Определяем ширину столбцов
        col_name_width = max(len(col) for col in numeric_cols) + 2
        value_width = 15

        # Шапка таблицы
        header = (f"{'Признак':<{col_name_width}} | "
                  f"{'Нижняя граница':^{value_width}} | "
                  f"{'Верхняя граница':^{value_width}} | "
                  f"{'Выбросы (кол-во)':^15} | "
                  f"{'Выбросы (%)':^10}")
        report.append(header)
        report.append("-" * len(header))

        for col in numeric_cols:
            q1 = self.data[col].quantile(0.25)
            q3 = self.data[col].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            outliers = self.data[(self.data[col] < lower_bound) | (self.data[col] > upper_bound)]
            count = len(outliers)
            outliers_count[col] = count

            # Форматируем строку с выравниванием
            row = (f"{col:<{col_name_width}} | "
                   f"{lower_bound:>{value_width}.2f} | "
                   f"{upper_bound:>{value_width}.2f} | "
                   f"{count:^15} | "
                   f"{count / len(self.data) * 100:^10.1f}%")
            report.append(row)

        # Добавляем пояснения
        report.append("\nПримечание:")
        report.append("- Q1: 25-й перцентиль, Q3: 75-й перцентиль")
        report.append("- IQR = Q3 - Q1 (межквартильный размах)")
        report.append("- Границы вычисляются как Q1 - 1.5*IQR и Q3 + 1.5*IQR")

        return report, outliers_count

    def get_missing_data_analysis_report(self):
        """Анализ пропущенных значений"""
        report = ["=== Анализ пропущенных значений ==="]
        total = len(self.data)
        missing = self.data.isnull().sum()
        missing = missing[missing > 0]

        if missing.empty:
            report.append("Пропущенных значений не обнаружено!")
        else:
            for col, count in missing.items():
                report.append(
                    f"{col}: пропущено {count} значений "
                    f"({count / total * 100:.1f}%)"
                )

        return report

    def get_cluster_analysis_report(self, features, n_clusters=3):
        """Кластерный анализ методом K-средних"""
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler

        report = ["=== Кластерный анализ (K-средних) ==="]
        report.append(f"Использованные признаки: {', '.join(features)}")
        report.append(f"Количество кластеров: {n_clusters}")

        # Масштабирование данных
        scaler = StandardScaler()
        scaled = scaler.fit_transform(self.data[features])

        # Кластеризация
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(scaled)

        # Анализ результатов
        self.data['Cluster'] = clusters
        cluster_stats = self.data.groupby('Cluster')[features].mean()

        report.append("\nСредние значения по кластерам:")
        report.append(cluster_stats.to_string())

        report.append("\n<--- 2D визуализация кластеров отображена во вкладке Визуализация")
        return report, clusters

    def get_correlation_matrix(self):
        # Выбираем только числовые колонки
        numeric_cols = self.data.select_dtypes(include=np.number).columns
        if len(numeric_cols) < 2:
            raise ValueError("Недостаточно числовых данных для анализа корреляций")
        # Считаем корреляционную матрицу
        corr_matrix = self.data[numeric_cols].corr()
        return corr_matrix



