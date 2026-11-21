# -*- coding: utf-8 -*-
"""GB/T 9124.1 法兰矢量图测试。"""

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

import main  # noqa: E402
from flange_drawing import render_gb_flange  # noqa: E402


class FlangeDrawingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        _head, cls.rows = main.load_csv(
            os.path.join(ROOT, 'Data', 'GBT9124_1_带颈对焊.csv'))

    def test_pn10_dn50(self):
        row = next(r for r in self.rows
                   if r['PN'] == '10' and r['DN'] == '50')
        pm = render_gb_flange(row, 1200, 900)
        self.assertIsNotNone(pm)
        self.assertEqual((pm.width(), pm.height()), (1200, 900))

    def test_all_pn10_sizes(self):
        for row in (r for r in self.rows if r['PN'] == '10'):
            pm = render_gb_flange(row, 600, 450, frame=False)
            self.assertIsNotNone(pm)
            self.assertFalse(pm.isNull())

    def test_gb9124_2_types(self):
        for file, kind in (
                ('GBT9124_2_带颈对焊.csv', 'WN'),
                ('GBT9124_2_带颈平焊.csv', 'SO'),
                ('GBT9124_2_整体.csv', 'IF'),
                ('GBT9124_2_承插焊.csv', 'SW'),
                ('GBT9124_2_螺纹.csv', 'TH'),
                ('GBT9124_2_法兰盖.csv', 'BL')):
            _h, rows = main.load_csv(os.path.join(ROOT, 'Data', file))
            row = next(r for r in rows if r.get('DN') == '50')
            pm = render_gb_flange(row, 600, 450, frame=False, kind=kind)
            self.assertIsNotNone(pm, kind)

    def test_pl_and_pj(self):
        for file, kind in (
                ('HGT20592_板式平焊.csv', 'PL'),
                ('HGT20592_对焊环松套.csv', 'PJ'),
                ('HGT20592_平焊环松套.csv', 'PJ')):
            _h, rows = main.load_csv(os.path.join(ROOT, 'Data', file))
            row = next(r for r in rows if r.get('DN') == '50')
            pm = render_gb_flange(row, 600, 450, frame=False, kind=kind)
            self.assertIsNotNone(pm, kind)


if __name__ == '__main__':
    unittest.main()
