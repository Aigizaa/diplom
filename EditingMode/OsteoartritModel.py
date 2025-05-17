import pandas as pd


class OsteoartritModel:
    def __init__(self):
        self.df = pd.DataFrame(columns=[
            "Врач",
            "Болезнь",
            "Сумма",
            "Возраст",
            "Рост",
            "Вес",
            "ИМТ",
            "ИМТ<25",
            "ГМС(1-9)",
            "ГМС(1-3)",
            "ГМС: легк.степ.",
            "ГМС: тяж.степ.",
            "Кожа: легк.степ.",
            "Кожа: тяж.степ.",
            "Келоидные рубцы",
            "Стрии",
            "Геморрагии",
            "Грыжи",
            "Птозы",
            "Хруст ВЧС",
            "Парадонтоз",
            "Долихостеномелия",
            "Кифоз/Лордоз",
            "Деф.гр.клетки",
            "Плоскостопие",
            "Вальгус стоп",
            "Хруст суставов",
            "ПМК",
            "Варикоз: легк.степ.",
            "Варикоз: тяж.степ.",
            "Миопия: легк.степ.",
            "Миопия: тяж.степ.",
            "Желч. пузырь",
            "ГЭРБ",
            "Гипотензия"
        ])

        self.num_of_columns = len(self.df.columns)

    def add_row(self, record):
        new_row = pd.DataFrame([record], columns=self.df.columns)
        self.df = pd.concat([self.df, new_row], ignore_index=True)

    def update_row(self, index, record):
        if 0 <= index < len(self.df):
            self.df.loc[index] = record

    def delete_row(self, index):
        if 0 <= index < len(self.df):
            self.df = self.df.drop(index).reset_index(drop=True)


