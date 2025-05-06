import pandas as pd


class OsteoartritModel:
    def __init__(self):
        self.df = pd.DataFrame(columns=[
            "Болезнь", "Возраст", "ДСТ", "Сумма", "ИМТ", "ГМС", "ГМС.2",
            "ИМТ<25", "кожа легк", "кожа тяж", "Келлоид", "Стрии", "Геморрагии",
            "Грыжи", "Птозы", "Хруст ВЧС", "Парадонтоз", "Долихостен",
            "ГМС легк", "ГМС выраж", "Кифоз/лордоз", "Деф гр клет", "Плоскост",
            "Вальг стопа", "Хруст суст", "ПМК", "Варик лег", "Варик тяж",
            "Миопия лег", "Миопия тяж", "Жел пуз.", "ГЭРБ", "Гипотенз"
        ])

    def add_record(self, record):
        new_row = pd.DataFrame([record], columns=self.df.columns)
        self.df = pd.concat([self.df, new_row], ignore_index=True)

    def update_record(self, index, record):
        if 0 <= index < len(self.df):
            self.df.loc[index] = record

    def delete_record(self, index):
        if 0 <= index < len(self.df):
            self.df = self.df.drop(index).reset_index(drop=True)


