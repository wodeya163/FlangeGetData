# -*- coding: utf-8 -*-
"""侧栏“选中规格尺寸列表”组件。"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QAbstractItemView, QHeaderView, QTableView)


class KvPanel(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('kv')
        self._model = QStandardItemModel(0, 2, self)
        self.setModel(self._model)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        hh = self.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        self.setMinimumHeight(6 * 26 + 10)

    def clear_rows(self):
        self._model.setRowCount(0)

    def set_rows(self, kv_rows, row):
        self._model.clear()
        self._model.setRowCount(len(kv_rows))
        for i, (col, lab) in enumerate(kv_rows):
            key = QStandardItem(lab)
            key.setForeground(QColor('#555'))
            key.setBackground(QColor('#f8fafc'))
            self._model.setItem(i, 0, key)
            value = QStandardItem(str(row.get(col, '') or '-'))
            font = value.font()
            font.setBold(True)
            value.setFont(font)
            self._model.setItem(i, 1, value)
        self.setMinimumHeight(min(max(len(kv_rows), 6) * 26 + 10, 300))
