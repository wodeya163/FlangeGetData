# -*- coding: utf-8 -*-
"""搜索/覆盖对话框 Model/View 测试。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

try:
    from PyQt5.QtWidgets import QApplication
except ImportError as exc:
    raise unittest.SkipTest('PyQt5 不可用：%s' % exc)

from ui.dialogs import CoverageDialog, SearchDialog  # noqa: E402


class DialogsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_search_dialog_model(self):
        def fake_search(text, limit=300, cache=None):
            return [('GB/T 9124.1', 'WN 带颈对焊', 'x.csv',
                     {'DN': '50', 'PN': '16'}, 'K=125')]
        dlg = SearchDialog(fake_search)
        dlg.query.setText('K=125')
        dlg.run_search()
        self.assertEqual(dlg.model.rowCount(), 1)
        self.assertEqual(dlg.model.item(0, 3).text(), '50')

    def test_coverage_dialog_model(self):
        dlg = CoverageDialog()
        self.assertGreaterEqual(dlg.model.rowCount(), 20)
        self.assertTrue(dlg.model.item(0, 0).text())


if __name__ == '__main__':
    unittest.main()
