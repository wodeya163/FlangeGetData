# -*- coding: utf-8 -*-
"""FIX-13：数值区间筛选的集成测试。"""

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
    import main
except ImportError as exc:
    raise unittest.SkipTest('PyQt5 不可用，跳过区间筛选测试：%s' % exc)


class RangeFilterTest(unittest.TestCase):
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
                if meta and meta[1] == 'GB17395_普通钢管.csv':
                    child = item
                    break
            if child is not None:
                break
        assert child is not None, '未找到 GB/T 17395 普通钢管页'
        cls.win.on_tree(child, 0)
        cls.total = len(cls.win.rows)

    @classmethod
    def tearDownClass(cls):
        cls.win.deleteLater()
        cls.app.processEvents()

    def test_range_widgets_exist(self):
        self.assertIn('D_o', self.win.range_widgets)
        self.assertIn('壁厚S(mm)', self.win.range_widgets)

    def test_range_filter_applies_and_resets(self):
        lo, hi = self.win.range_widgets['D_o']
        lo.setText('100')
        hi.setText('200')
        self.win._filter_timer.stop()
        rows = self.win._filtered_rows()
        self.assertTrue(rows)
        self.assertLess(len(rows), self.total)
        for r in rows:
            self.assertGreaterEqual(float(r['D_o']), 100)
            self.assertLessEqual(float(r['D_o']), 200)
        self.assertIn('外径', self.win.chips.text())

        self.win.reset_filters()
        self.win._filter_timer.stop()
        self.assertEqual(len(self.win._filtered_rows()), self.total)

    def test_in_range_helper(self):
        self.assertTrue(main._in_range('150', 100, 200))
        self.assertFalse(main._in_range('250', 100, 200))
        self.assertFalse(main._in_range('-', 100, 200))
        self.assertTrue(main._in_range('0.5', None, 1))
        self.assertTrue(main._in_range('0.5', 0, None))


if __name__ == '__main__':
    unittest.main()
