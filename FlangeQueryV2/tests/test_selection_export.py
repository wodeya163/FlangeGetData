# -*- coding: utf-8 -*-
"""FIX-14：多选、剪贴板与列宽记忆的 GUI 测试。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication, QTableWidgetSelectionRange
    import main
except ImportError as exc:
    raise unittest.SkipTest('PyQt5 不可用，跳过多选测试：%s' % exc)


class SelectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.win = main.MainWindow()
        child = None
        for i in range(cls.win.tree.topLevelItemCount()):
            top = cls.win.tree.topLevelItem(i)
            for j in range(top.childCount()):
                item = top.child(j)
                meta = item.data(0, Qt.UserRole)
                if meta and meta[1] == 'HGT20592_带颈对焊.csv':
                    child = item
                    break
            if child is not None:
                break
        assert child is not None
        cls.win.on_tree(child, 0)

    @classmethod
    def tearDownClass(cls):
        cls.win.deleteLater()
        cls.app.processEvents()

    def test_single_selection_returns_one_row(self):
        self.win.table.clearSelection()
        self.win.table.selectRow(0)
        rows = self.win._selected_rows()
        self.assertEqual(len(rows), 1)

    def test_range_selection_returns_multiple_rows(self):
        self.win.table.clearSelection()
        last_col = self.win.table.columnCount() - 1
        self.win.table.setRangeSelected(
            QTableWidgetSelectionRange(0, 0, 2, last_col), True)
        rows = self.win._selected_rows()
        self.assertEqual(len(rows), 3)

    def test_copy_selected_rows_to_clipboard(self):
        self.win.table.clearSelection()
        self.win.table.selectRow(0)
        self.win.copy_selected_rows()
        text = QApplication.clipboard().text()
        self.assertIn('DN', text.splitlines()[0])
        self.assertEqual(len(text.strip().splitlines()), 2)

    def test_header_state_saved_and_restored(self):
        header = self.win.table.horizontalHeader()
        header.resizeSection(0, 77)
        self.win._save_header_state()
        header.resizeSection(0, 20)
        self.win._restore_header_state('HGT20592_带颈对焊.csv')
        self.assertEqual(header.sectionSize(0), 77)


if __name__ == '__main__':
    unittest.main()
