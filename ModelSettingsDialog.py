from PySide6.QtWidgets import (QDialog, QFormLayout, QSpinBox, QDoubleSpinBox,
                              QComboBox, QPushButton, QHBoxLayout)
# Класс для настроек модели машинного обучения
class ModelSettingsDialog(QDialog):
    def __init__(self, model_type, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Настройки модели: {model_type}")
        self.model_type = model_type
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        if self.model_type == "Случайный лес":
            self.n_estimators = QSpinBox()
            self.n_estimators.setRange(10, 500)
            self.n_estimators.setValue(100)
            layout.addRow("Количество деревьев:", self.n_estimators)

            self.max_depth = QSpinBox()
            self.max_depth.setRange(1, 100)
            self.max_depth.setValue(10)
            layout.addRow("Макс. глубина:", self.max_depth)

            self.min_samples_split = QSpinBox()
            self.min_samples_split.setRange(2, 20)
            self.min_samples_split.setValue(2)
            layout.addRow("Мин. образцов для разделения:", self.min_samples_split)

        elif self.model_type == "Логистическая регрессия":
            self.C = QDoubleSpinBox()
            self.C.setRange(0.01, 10.0)
            self.C.setValue(1.0)
            self.C.setSingleStep(0.1)
            layout.addRow("Параметр C:", self.C)

            self.max_iter = QSpinBox()
            self.max_iter.setRange(100, 10000)
            self.max_iter.setValue(1000)
            layout.addRow("Макс. итераций:", self.max_iter)

        #elif self.model_type == "Линейная регрессия":
        #    self.fit_intercept = QCheckBox()
        #    self.fit_intercept.setChecked(True)
        #    layout.addRow("Подгонка intercept:", self.fit_intercept)

        elif self.model_type == "K-ближайших соседей (KNN)":
            self.n_neighbors = QSpinBox()
            self.n_neighbors.setRange(1, 50)
            self.n_neighbors.setValue(5)
            layout.addRow("Количество соседей:", self.n_neighbors)

            self.weights = QComboBox()
            self.weights.addItems(["uniform", "distance"])
            layout.addRow("Весовая функция:", self.weights)

        elif self.model_type == "Дерево решений":
            self.max_depth_tree = QSpinBox()
            self.max_depth_tree.setRange(1, 100)
            self.max_depth_tree.setValue(5)
            layout.addRow("Макс. глубина:", self.max_depth_tree)

            self.min_samples_split_tree = QSpinBox()
            self.min_samples_split_tree.setRange(2, 20)
            self.min_samples_split_tree.setValue(2)
            layout.addRow("Мин. образцов для разделения:", self.min_samples_split_tree)

        # Кнопки
        btn_box = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)

        layout.addRow(btn_box)
        self.setLayout(layout)

    def get_settings(self):
        settings = {}
        if self.model_type == "Случайный лес":
            settings.update({
                'n_estimators': self.n_estimators.value(),
                'max_depth': self.max_depth.value(),
                'min_samples_split': self.min_samples_split.value()
            })
        elif self.model_type == "Логистическая регрессия":
            settings.update({
                'C': self.C.value(),
                'max_iter': self.max_iter.value()
            })
        elif self.model_type == "Линейная регрессия":
            settings.update({
                'fit_intercept': self.fit_intercept.isChecked()
            })
        elif self.model_type == "K-ближайших соседей (KNN)":
            settings.update({
                'n_neighbors': self.n_neighbors.value(),
                'weights': self.weights.currentText()
            })
        elif self.model_type == "Дерево решений":
            settings.update({
                'max_depth': self.max_depth_tree.value(),
                'min_samples_split': self.min_samples_split_tree.value()
            })
        return settings
