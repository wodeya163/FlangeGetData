# -*- coding: utf-8 -*-
"""QAbstractTableModel 基础测试。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication
except ImportError as exc:
    raise unittest.SkipTest('PyQt5 不可用：%s' % exc)

from ui.table_model import FlangeTableModel  # noqa: E402


class TableModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.model = FlangeTableModel(
            [('DN', '公称尺寸'), ('D', '外径 D')],
            [{'DN': '50', 'D': '165'}, {'DN': '100', 'D': '220'}])

    def test_shape_and_display(self):
        self.assertEqual(self.model.rowCount(), 2)
        self.assertEqual(self.model.columnCount(), 2)
        idx = self.model.index(0, 1)
        self.assertEqual(self.model.data(idx, Qt.DisplayRole), '165')
        self.assertEqual(self.model.headerData(0, Qt.Horizontal), '公称尺寸')

    def test_row_at_and_sort(self):
        self.assertEqual(self.model.row_at(0)['DN'], '50')
        self.model.sort_by('DN', ascending=False)
        self.assertEqual(self.model.row_at(0)['DN'], '100')


if __name__ == '__main__':
    unittest.main()
