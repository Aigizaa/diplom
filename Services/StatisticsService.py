import pandas as pd
import numpy as np
from PySide6.QtWidgets import QMessageBox


class StatisticsService:
    def __init__(self, data: pd.DataFrame, parent_ui=None):
        self.view = parent_ui
        self.data = data

    def get_statistics(self) -> pd.DataFrame:
        # Фильтруем только числовые столбцы
        numeric_data = self.data.select_dtypes(include=np.number)
        if numeric_data.empty:
            QMessageBox.critical(self.view, "Ошибка", "Нет числовых данных для анализа!")

        # Словарь для переименования строк
        rename_dict = {
            "count": "Количество",
            "mean": "Среднее",
            "std": "Станд. отклонение",
            "min": "Минимум",
            "25%": "25-й перцентиль",
            "50%": "Медиана",
            "75%": "75-й перцентиль",
            "max": "Максимум"
        }
        stats_df = numeric_data.describe(include=np.number).round(3)
        stats_df_renamed = stats_df.rename(index=rename_dict)

        # Доп. статистика (мода, skew, kurtosis и т.д.)
        skew_row = pd.DataFrame(numeric_data.skew().round(3)).T.rename(index={0: "Асимметрия"})
        kurtosis_row = pd.DataFrame(numeric_data.kurtosis().round(3)).T.rename(index={0: "Эксцесс"})

        # Объединяем со stats_df
        stats_df_extended = pd.concat([stats_df_renamed, skew_row, kurtosis_row])

        return stats_df_extended.transpose()
