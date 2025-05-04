from PySide6.QtCore import Qt, QAbstractTableModel


# 3. Модели данных
class PandasModel(QAbstractTableModel):
    """Модель для отображения DataFrame в QTableView"""
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            else:
                return str(self._data.index[section])
        return None

    def sort(self, column, order):
        """Базовая сортировка"""
        if 0 <= column < self.columnCount():
            colname = self._data.columns[column]
            self._data = self._data.sort_values(
                colname,
                ascending=(order == Qt.AscendingOrder),
                kind='mergesort'
            )
            self.layoutChanged.emit()
