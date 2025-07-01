import pandas as pd
import numpy as np
from PySide6.QtWidgets import QMessageBox


class StatisticsService:
    def __init__(self, data: pd.DataFrame, parent_ui=None):
        self.view = parent_ui
        self.data = data

    def get_statistics(self) -> pd.DataFrame:
        stats_list = []
        # Фильтруем только числовые столбцы
        numeric_data = self.data.select_dtypes(include=np.number)
        if numeric_data.empty:
            QMessageBox.critical(self.view, "Ошибка", "Нет числовых данных для статистики!")

        # Словарь для переименования строк
        rename_dict = {
            "count": "Количество",
            "mean": "Среднее",
            "std": "Станд. отклонение",
            "min": "Минимум",
            "25%": "25-й процентиль",
            "50%": "Медиана",
            "75%": "75-й процентиль",
            "max": "Максимум"
        }
        stats_df = numeric_data.describe(include=np.number).round(3)
        stats_df_renamed = stats_df.rename(index=rename_dict)

        # Доп. статистика (мода, skew, kurtosis и т.д.)
        skew_row = pd.DataFrame(numeric_data.skew().round(3)).T.rename(index={0: "Асимметрия"})
        kurtosis_row = pd.DataFrame(numeric_data.kurtosis().round(3)).T.rename(index={0: "Эксцесс"})
        mode_row = pd.DataFrame(numeric_data.mode().iloc[0].round(3)).T.rename(index={0: "Мода"})
        frequency_row = pd.DataFrame(numeric_data.sum().round(3)).T.rename(index={0: "Частота"})
        rel_frequency_row = pd.DataFrame((numeric_data.sum() / len(numeric_data) * 100).round(3)).T.rename(
            index={0: "Отн. частота"})

        # Объединяем со stats_df
        stats_df_extended = pd.concat(
            [stats_df_renamed, skew_row, kurtosis_row, mode_row, frequency_row, rel_frequency_row])

        return stats_df_extended.transpose()

    def _get_numeric_stats(self, numeric_data: pd.DataFrame) -> pd.DataFrame:
        # Словарь для переименования строк
        rename_dict = {
            "count": "Количество",
            "mean": "Среднее",
            "std": "Станд. отклонение",
            "min": "Минимум",
            "25%": "25-й процентиль",
            "50%": "Медиана",
            "75%": "75-й процентиль",
            "max": "Максимум"
        }
        stats_df = numeric_data.describe(include=np.number).round(3)
        stats_df_renamed = stats_df.rename(index=rename_dict)

        # Доп. статистика (мода, skew, kurtosis и т.д.)
        skew_row = pd.DataFrame(numeric_data.skew().round(3)).T.rename(index={0: "Асимметрия"})
        kurtosis_row = pd.DataFrame(numeric_data.kurtosis().round(3)).T.rename(index={0: "Эксцесс"})
        mode_row = pd.DataFrame(numeric_data.mode().iloc[0].round(3)).T.rename(index={0: "Мода"})
        frequency_row = pd.DataFrame(numeric_data.sum().round(3)).T.rename(index={0: "Частота"})
        rel_frequency_row = pd.DataFrame((numeric_data.sum()/len(numeric_data) * 100).round(3)).T.rename(index={0: "Отн. частота"})

        # Объединяем со stats_df
        stats_df_extended = pd.concat([stats_df_renamed, skew_row, kurtosis_row, mode_row, frequency_row, rel_frequency_row])

        return stats_df_extended.transpose()

    def _get_categorical_stats(self, data: pd.DataFrame) -> pd.DataFrame:
        stats = []
        for col in data.columns:
            value_counts = data[col].value_counts()
            total = value_counts.sum()

            # Для бинарных данных (0/1 или True/False)
            if set(data[col].dropna().unique()) <= {0, 1, True, False}:
                # Преобразуем в 0/1 для удобства
                binary_series = data[col].replace({True: 1, False: 0}).dropna()
                stats.append({
                    "Переменная": col,
                    "Тип": "Бинарная",
                    "Количество": total,
                    "Частота": binary_series.sum(),
                    "Отн. частота": f"{(binary_series.sum() / total * 100):.1f}%",
                    "Мода": value_counts.idxmax()
                })
            else:
                # Для обычных категориальных данных
                top_value = value_counts.index[0]
                top_freq = value_counts.iloc[0]
                stats.append({
                    "Переменная": col,
                    "Тип": "Категориальная",
                    "Количество": total,
                    "Уникальные": len(value_counts),
                    "Мода": top_value,
                    "Частота моды": top_freq,
                    "Отн. частота моды": f"{(top_freq / total * 100):.1f}%"
                })

        return pd.DataFrame(stats).set_index("Переменная")

