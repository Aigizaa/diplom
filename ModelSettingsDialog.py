from PySide6.QtWidgets import (QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox, QPushButton, QHBoxLayout)


class ModelSettingsData:
    def __init__(self):
        # Храним настройки для всех типов моделей
        self._settings = {
            "Случайный лес": {
                'n_estimators': 100,
                'max_depth': 10,
                'min_samples_split': 2,
                'min_samples_leaf': 1
            },
            "Логистическая регрессия": {
                'C': 1.0,
                'max_iter': 1000
            },
            "K-ближайших соседей (KNN)": {
                'n_neighbors': 5,
                'weights': 'uniform'
            },
            "Дерево решений": {
                'max_depth': 5,
                'min_samples_split': 2,
                'min_samples_leaf': 1
            }
        }

    def get_settings(self, model_type):
        """Возвращает настройки для указанного типа модели"""
        return self._settings.get(model_type, {}).copy()

    def update_settings(self, model_type, new_settings):
        """Обновляет настройки для указанного типа модели"""
        if model_type in self._settings:
            self._settings[model_type].update(new_settings)


class ModelSettingsView(QDialog):
    def __init__(self, model_type, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Настройки модели: {model_type}")
        self.model_type = model_type
        self.presenter = None

        # UI элементы
        self.n_estimators = QSpinBox()
        self.max_depth = QSpinBox()
        self.min_samples_split = QSpinBox()
        self.min_samples_leaf = QSpinBox()
        self.C = QDoubleSpinBox()
        self.max_iter = QSpinBox()
        self.n_neighbors = QSpinBox()
        self.weights = QComboBox()
        self.max_depth_tree = QSpinBox()
        self.min_samples_split_tree = QSpinBox()
        self.min_samples_leaf_tree = QSpinBox()

        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        if self.model_type == "Случайный лес":
            self.n_estimators.setRange(10, 500)
            layout.addRow("Количество деревьев:", self.n_estimators)

            self.max_depth.setRange(1, 100)
            layout.addRow("Макс. глубина деревьев:", self.max_depth)

            self.min_samples_split.setRange(2, 20)
            layout.addRow("Мин. элементов для разделения:", self.min_samples_split)

            self.min_samples_leaf.setRange(1, 20)
            layout.addRow("Мин. элементов в листе:", self.min_samples_leaf)

        elif self.model_type == "Логистическая регрессия":
            self.C.setRange(0.01, 10.0)
            self.C.setSingleStep(0.1)
            layout.addRow("Штраф C:", self.C)

            self.max_iter.setRange(100, 10000)
            layout.addRow("Макс. итераций:", self.max_iter)

        elif self.model_type == "K-ближайших соседей (KNN)":
            self.n_neighbors.setRange(1, 50)
            layout.addRow("Количество соседей:", self.n_neighbors)

            self.weights.addItems(["uniform", "distance"])
            layout.addRow("Весовая функция:", self.weights)

        elif self.model_type == "Дерево решений":
            self.max_depth_tree.setRange(1, 100)
            layout.addRow("Макс. глубина:", self.max_depth_tree)

            self.min_samples_split_tree.setRange(2, 20)
            layout.addRow("Мин. элементов для разделения:", self.min_samples_split_tree)

            self.min_samples_leaf_tree.setRange(1, 20)
            layout.addRow("Мин. элементов в листе:", self.min_samples_leaf_tree)

        # Кнопки
        btn_box = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self._on_accept)
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_ok)
        btn_box.addWidget(btn_cancel)

        layout.addRow(btn_box)
        self.setLayout(layout)

    def _on_accept(self):
        if self.presenter:
            self.presenter.save_settings()
        self.accept()

    def set_presenter(self, presenter):
        self.presenter = presenter

    def get_current_settings(self):
        """Возвращает текущие значения полей в виде словаря"""
        settings = {}
        if self.model_type == "Случайный лес":
            settings.update({
                'n_estimators': self.n_estimators.value(),
                'max_depth': self.max_depth.value(),
                'min_samples_split': self.min_samples_split.value(),
                'min_samples_leaf': self.min_samples_leaf.value()
            })
        elif self.model_type == "Логистическая регрессия":
            settings.update({
                'C': self.C.value(),
                'max_iter': self.max_iter.value()
            })
        elif self.model_type == "K-ближайших соседей (KNN)":
            settings.update({
                'n_neighbors': self.n_neighbors.value(),
                'weights': self.weights.currentText()
            })
        elif self.model_type == "Дерево решений":
            settings.update({
                'max_depth': self.max_depth_tree.value(),
                'min_samples_split': self.min_samples_split_tree.value(),
                'min_samples_leaf': self.min_samples_leaf_tree.value()
            })
        return settings

    def load_settings(self, settings):
        """Загружает настройки модели в UI элементы"""
        if self.model_type == "Случайный лес":
            self.n_estimators.setValue(settings.get('n_estimators', 100))
            self.max_depth.setValue(settings.get('max_depth', 10))
            self.min_samples_split.setValue(settings.get('min_samples_split', 2))
            self.min_samples_leaf.setValue(settings.get('min_samples_leaf', 1))

        elif self.model_type == "Логистическая регрессия":
            self.C.setValue(settings.get('C', 1.0))
            self.max_iter.setValue(settings.get('max_iter', 1000))

        elif self.model_type == "K-ближайших соседей (KNN)":
            self.n_neighbors.setValue(settings.get('n_neighbors', 5))
            self.weights.setCurrentText(settings.get('weights', 'uniform'))

        elif self.model_type == "Дерево решений":
            self.max_depth_tree.setValue(settings.get('max_depth', 5))
            self.min_samples_split_tree.setValue(settings.get('min_samples_split', 2))
            self.min_samples_leaf_tree.setValue(settings.get('min_samples_leaf', 1))


class ModelSettingsPresenter:
    def __init__(self, view: ModelSettingsView, model: ModelSettingsData):
        self.view = view
        self.model = model
        self.view.set_presenter(self)

        # Загружаем текущие настройки в view
        self._load_current_settings()

    def _load_current_settings(self):
        """Загружает текущие настройки модели в view"""
        settings = self.model.get_settings(self.view.model_type)
        self.view.load_settings(settings)

    def save_settings(self):
        """Сохраняет изменения настроек"""
        new_settings = self.view.get_current_settings()
        self.model.update_settings(self.view.model_type, new_settings)
