# -*- coding: utf-8 -*-
"""DataTable（QTableView 适配器）兼容 API 测试。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import (QApplication, QTableWidgetItem,
                                 QTableWidgetSelectionRange)
except ImportError as exc:
    raise unittest.SkipTest('PyQt5 不可用：%s' % exc)

import main  # noqa: E402
from ui.data_table import DataTable  # noqa: E402


class DataTableTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def make_table(self):
        table = DataTable()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(['DN', 'D'])
        table.setRowCount(2)
        for i, (dn, d) in enumerate((('50', '165'), ('100', '220'))):
            table.setItem(i, 0, main.NumItem(dn, float(dn)))
            table.setItem(i, 1, QTableWidgetItem(d))
        return table

    def test_item_and_selection(self):
        table = self.make_table()
        self.assertEqual(table.rowCount(), 2)
        self.assertEqual(table.item(0, 0).text(), '50')
        table.selectRow(0)
        self.assertEqual(table.currentRow(), 0)
        self.assertEqual(table.item(0, 0).data(Qt.UserRole), None)

    def test_sort(self):
        table = self.make_table()
        table.setSortingEnabled(True)
        table.sortItems(0, Qt.DescendingOrder)
        self.assertEqual(table.item(0, 0).text(), '100')

    def test_range_selection(self):
        table = self.make_table()
        table.setRangeSelected(QTableWidgetSelectionRange(0, 0, 1, 1), True)
        self.assertEqual(len(table.selectedItems()), 4)


if __name__ == '__main__':
    unittest.main()
