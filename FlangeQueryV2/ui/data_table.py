# -*- coding: utf-8 -*-
"""QTableView + QAbstractTableModel 适配器。

对外保留主窗口现有用到的 QTableWidget 风格 API（setItem/item/selectRow 等），
内部改为模型驱动，便于后续彻底移除 QTableWidget。
"""

from PyQt5.QtCore import (QAbstractTableModel, QItemSelection,
                          QItemSelectionModel, QModelIndex, Qt, pyqtSignal)
from PyQt5.QtWidgets import QTableView


class CellTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.headers = []
        self.cells = []   # cells[row][col] = (text, rowdata, sortval, align)
        self._bulk = False

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.cells)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if index.row() >= len(self.cells) or index.column() >= len(self.cells[index.row()]):
            return None
        cell = self.cells[index.row()][index.column()]
        if role == Qt.DisplayRole:
            return cell[0]
        if role == Qt.UserRole:
            return cell[1]
        if role == Qt.TextAlignmentRole:
            return cell[3]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            if 0 <= section < len(self.headers):
                return self.headers[section]
            return ''
        return str(section + 1)

    def set_headers(self, labels):
        self.beginResetModel()
        self.headers = list(labels)
        self.cells = [[('', None, '', Qt.AlignCenter) for _ in self.headers]
                      for _ in self.cells]
        self.endResetModel()

    def set_column_count(self, count):
        if count == len(self.headers):
            return
        self.beginResetModel()
        if count < len(self.headers):
            self.headers = self.headers[:count]
            for row in self.cells:
                del row[count:]
        else:
            self.headers += [''] * (count - len(self.headers))
            for row in self.cells:
                row.extend([('', None, '', Qt.AlignCenter)] * (count - len(row)))
        self.endResetModel()

    def set_row_count(self, count):
        if count == len(self.cells):
            return
        self.beginResetModel()
        if count < len(self.cells):
            del self.cells[count:]
        else:
            for _ in range(count - len(self.cells)):
                self.cells.append([('', None, '', Qt.AlignCenter)
                                   for _ in self.headers])
        self.endResetModel()

    def set_cell(self, row, col, text, rowdata, sortval, align):
        if row >= len(self.cells) or col >= len(self.headers):
            return
        self.cells[row][col] = (text, rowdata, sortval, align)
        if self._bulk:
            return
        idx = self.index(row, col)
        self.dataChanged.emit(idx, idx, [Qt.DisplayRole, Qt.UserRole,
                                         Qt.TextAlignmentRole])

    def set_bulk(self, enabled):
        if self._bulk and not enabled:
            self._bulk = False
            if self.cells and self.headers:
                self.dataChanged.emit(
                    self.index(0, 0),
                    self.index(len(self.cells) - 1, len(self.headers) - 1))
        else:
            self._bulk = enabled

    def clear(self):
        self.beginResetModel()
        self.headers = []
        self.cells = []
        self.endResetModel()

    def sort(self, column, order=Qt.AscendingOrder):
        if not self.cells or column < 0 or column >= len(self.headers):
            return
        self.layoutAboutToBeChanged.emit()

        def key(row):
            value = row[column][2]
            try:
                return (0, float(str(value).replace(',', '.')), '')
            except (TypeError, ValueError):
                return (1, 0, str(value))

        self.cells.sort(key=key, reverse=(order == Qt.DescendingOrder))
        self.layoutChanged.emit()


class CompatItem:
    def __init__(self, table, row, col):
        self._table = table
        self._row = row
        self._col = col

    def row(self):
        return self._row

    def column(self):
        return self._col

    def text(self):
        return self._table.model().cells[self._row][self._col][0]

    def data(self, role):
        return self._table.model().data(
            self._table.model().index(self._row, self._col), role)


class DataTable(QTableView):
    """兼容主窗口现有 QTableWidget 调用的 QTableView。"""

    itemSelectionChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = CellTableModel(self)
        self.setModel(self._model)
        self.selectionModel().selectionChanged.connect(
            lambda *_: self.itemSelectionChanged.emit())
        self._sort_enabled = False
        self._sort_col = -1
        self._sort_order = Qt.AscendingOrder
        self.horizontalHeader().sectionClicked.connect(self._on_header_clicked)

    def setSortingEnabled(self, enabled):
        # 不调用 QTableView 的自动排序：它会在 setSortingEnabled(True) 时
        # 立即按当前列重排，覆盖 fill_table 随后的“按 DN 升序”。
        self._sort_enabled = bool(enabled)
        self.horizontalHeader().setSortIndicatorShown(bool(enabled))

    def _on_header_clicked(self, column):
        if not self._sort_enabled:
            return
        if column == self._sort_col:
            order = (Qt.DescendingOrder if self._sort_order == Qt.AscendingOrder
                     else Qt.AscendingOrder)
        else:
            order = Qt.AscendingOrder
        self.sortItems(column, order)

    def model(self):
        return self._model

    def setUpdatesEnabled(self, enabled):
        super().setUpdatesEnabled(enabled)
        self._model.set_bulk(not enabled)

    def rowCount(self):
        return self._model.rowCount()

    def columnCount(self):
        return self._model.columnCount()

    def setRowCount(self, count):
        self._model.set_row_count(count)

    def setColumnCount(self, count):
        self._model.set_column_count(count)

    def setHorizontalHeaderLabels(self, labels):
        self._model.set_headers(labels)

    def setItem(self, row, col, item):
        text = item.text()
        rowdata = item.data(Qt.UserRole)
        sortval = getattr(item, '_sv', text)
        align = item.textAlignment()
        self._model.set_cell(row, col, text, rowdata, sortval, align)

    def item(self, row, col):
        if row < 0 or col < 0 or row >= self.rowCount() \
                or col >= self.columnCount():
            return None
        return CompatItem(self, row, col)

    def selectedItems(self):
        return [CompatItem(self, idx.row(), idx.column())
                for idx in self.selectedIndexes()]

    def currentRow(self):
        idx = self.currentIndex()
        return idx.row() if idx.isValid() else -1

    def clear(self):
        self._model.clear()

    def clearContents(self):
        self._model.clear()

    def sortItems(self, column, order=Qt.AscendingOrder):
        self._model.sort(column, order)
        self._sort_col = column
        self._sort_order = order
        self.horizontalHeader().setSortIndicator(column, order)

    def scrollToItem(self, item):
        self.scrollTo(self._model.index(item.row(), item.column()))

    def setRangeSelected(self, selection_range, selected):
        top, left = selection_range.topRow(), selection_range.leftColumn()
        bottom = selection_range.bottomRow()
        right = selection_range.rightColumn()
        selection = QItemSelection(self._model.index(top, left),
                                   self._model.index(bottom, right))
        mode = QItemSelectionModel.Select if selected else QItemSelectionModel.Deselect
        self.selectionModel().select(selection, mode)
