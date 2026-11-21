# -*- coding: utf-8 -*-
"""KvPanel 侧栏组件测试。"""

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

from ui.kv_panel import KvPanel  # noqa: E402


class KvPanelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_rows_and_values(self):
        panel = KvPanel()
        panel.set_rows([('DN', '公称尺寸 DN'), ('D', '外径 D')],
                       {'DN': '50', 'D': '165'})
        self.assertEqual(panel.model().rowCount(), 2)
        self.assertEqual(panel.model().item(1, 1).text(), '165')
        panel.clear_rows()
        self.assertEqual(panel.model().rowCount(), 0)


if __name__ == '__main__':
    unittest.main()
