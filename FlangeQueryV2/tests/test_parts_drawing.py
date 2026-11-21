# -*- coding: utf-8 -*-
"""垫片/钢管/管件/密封面矢量图测试。"""

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
from parts_drawing import (render_container, render_fitting, render_gasket,
                           render_pipe, render_seal)  # noqa: E402


class PartsDrawingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def row(self, name, **where):
        _head, rows = main.load_csv(os.path.join(ROOT, 'Data', name))
        return next(r for r in rows
                    if all(str(r.get(k)) == str(v) for k, v in where.items()))

    def test_parts(self):
        cases = [
            (render_gasket, 'HGT20606_RF.csv', 'gasket_flat.bmp'),
            (render_gasket, 'HGT20612.csv', 'gasket_ring.bmp'),
            (render_pipe, 'GB17395_普通钢管.csv', 'pipe.bmp'),
            (render_fitting, 'GB12459_弯头.csv', 'fittings_elbow.bmp'),
            (render_fitting, 'GB12459_三通.csv', 'fittings_tee.bmp'),
            (render_fitting, 'GB12459_异径管.csv', 'fittings_reducer.bmp'),
            (render_fitting, 'GB12459_管帽.csv', 'fittings_cap.bmp'),
            (render_seal, 'mfm_RF.csv', 'mfm_突面.bmp'),
            (render_container, 'NBT47023_带颈对焊.csv', '容器法兰.bmp'),
        ]
        for fn, csvf, tpl in cases:
            pm = fn(self.row(csvf), tpl)
            self.assertIsNotNone(pm, tpl)
        elbow = self.row('GB12459_弯头.csv')
        for ang in (45, 90, 180):
            self.assertIsNotNone(
                render_fitting(elbow, 'fittings_elbow.bmp', angle=ang))


if __name__ == '__main__':
    unittest.main()
