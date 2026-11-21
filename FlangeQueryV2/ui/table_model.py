# -*- coding: utf-8 -*-
"""QAbstractTableModel 基础实现，供后续替换 QTableWidget。"""

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt


class FlangeTableModel(QAbstractTableModel):
    def __init__(self, columns=None, rows=None, parent=None):
        super().__init__(parent)
        self._columns = list(columns or [])
        self._rows = list(rows or [])

    def set_data(self, columns, rows):
        self.beginResetModel()
        self._columns = list(columns)
        self._rows = list(rows)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        key = self._columns[index.column()][0]
        value = self._rows[index.row()].get(key, '')
        return '' if value is None else str(value)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._columns[section][1]
        return str(section + 1)

    def row_at(self, row):
        return self._rows[row]

    def sort_by(self, key, ascending=True):
        def sort_key(row):
            value = str(row.get(key, '')).replace(',', '.')
            try:
                return (0, float(value), '')
            except ValueError:
                return (1, 0, value)

        self.layoutAboutToBeChanged.emit()
        self._rows.sort(key=sort_key, reverse=not ascending)
        self.layoutChanged.emit()
