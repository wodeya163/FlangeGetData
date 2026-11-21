# -*- coding: utf-8 -*-
"""波纹伸缩节参数化矢量渲染测试。"""

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
from bellows_drawing import pipeline, render_bellows  # noqa: E402


class BellowsDrawingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        _head, cls.rows = main.load_csv(
            os.path.join(ROOT, 'Data', 'U_bellows.csv'))

    def test_pipeline_spec(self):
        _spec, od, wall = pipeline({'接管规格': 'φ219×6'})
        self.assertEqual(od, 219.0)
        self.assertEqual(wall, 6.0)

    def test_render_all_sizes(self):
        for row in (self.rows[0], self.rows[8], self.rows[-1]):
            pm = render_bellows(row, 600, 380)
            self.assertFalse(pm.isNull())
            self.assertEqual((pm.width(), pm.height()), (600, 380))

    def test_frame_render(self):
        pm = render_bellows(self.rows[0], 1200, 900, frame=True)
        self.assertEqual((pm.width(), pm.height()), (1200, 900))

    def test_card_vector_labels_are_separate(self):
        import ui.drawing_card as drawing_card
        old = drawing_card.VECTOR_ENABLED
        drawing_card.VECTOR_ENABLED = True
        try:
            card = main.DrawingCard()
            card.show_page('bellows.bmp', main.BELLOWS_LABELS, self.rows[0])
            self.assertTrue(card._vector)
            self.assertGreaterEqual(len(card.labels), 1)
            card.deleteLater()
        finally:
            drawing_card.VECTOR_ENABLED = old


if __name__ == '__main__':
    unittest.main()
