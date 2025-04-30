from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QComboBox, QLineEdit, QPushButton
class FilterDialog(QDialog):
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Фильтрация данных")
        self.columns = columns
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.column_combo = QComboBox()
        self.column_combo.addItems(self.columns)
        form_layout.addRow("Столбец:", self.column_combo)

        self.operator_combo = QComboBox()
        self.operator_combo.addItems([">", ">=", "==", "<=", "<", "!=", "содержит"])
        form_layout.addRow("Оператор:", self.operator_combo)

        self.value_edit = QLineEdit()
        form_layout.addRow("Значение:", self.value_edit)

        layout.addLayout(form_layout)

        self.btn_apply = QPushButton("Применить фильтр")
        self.btn_apply.clicked.connect(self.accept)
        layout.addWidget(self.btn_apply)

        self.setLayout(layout)

    def get_filter(self):
        return {
            'column': self.column_combo.currentText(),
            'operator': self.operator_combo.currentText(),
            'value': self.value_edit.text()
        }
