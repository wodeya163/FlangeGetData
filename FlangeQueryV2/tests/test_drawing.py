# -*- coding: utf-8 -*-
"""FIX-18：参数化矢量法兰图的渲染测试。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

try:
    from PyQt5.QtGui import QColor
    from PyQt5.QtWidgets import QApplication
    import main
    from drawing import render_flange
except ImportError as exc:
    raise unittest.SkipTest('PyQt5 不可用，跳过矢量绘图测试：%s' % exc)


class VectorDrawingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        _head, rows = main.load_csv(
            os.path.join(ROOT, 'Data', 'HGT20592_带颈对焊.csv'))
        cls.row = rows[1]  # PN16 DN50，尺寸齐全

    def test_render_returns_pixmap_with_ink(self):
        pixmap = render_flange(self.row)
        self.assertIsNotNone(pixmap)
        self.assertFalse(pixmap.isNull())
        self.assertEqual((pixmap.width(), pixmap.height()), (596, 498))
        image = pixmap.toImage()
        ink = 0
        white = QColor('white').name()
        for x in range(0, image.width(), 8):
            for y in range(0, image.height(), 8):
                if image.pixelColor(x, y).name() != white:
                    ink += 1
        self.assertGreater(ink, 50)

    def test_missing_dimensions_returns_none(self):
        self.assertIsNone(render_flange({}))
        self.assertIsNone(render_flange({'D': '100'}))

    def test_card_uses_vector_instead_of_bmp_labels(self):
        import ui.drawing_card as drawing_card
        old = drawing_card.FLANGE_VECTOR_ENABLED
        drawing_card.FLANGE_VECTOR_ENABLED = True
        try:
            card = main.DrawingCard()
            card.show_page('WN-带颈对焊.bmp', main.WN_LABELS, self.row)
            self.assertTrue(card._vector)
            self.assertFalse(card.pic.pixmap().isNull())
            self.assertFalse(card.pic.pixmap().isNull())
            card.deleteLater()
        finally:
            drawing_card.FLANGE_VECTOR_ENABLED = old

    def test_flange_vector_can_fallback_to_bmp(self):
        import ui.drawing_card as drawing_card
        old = drawing_card.FLANGE_VECTOR_ENABLED
        drawing_card.FLANGE_VECTOR_ENABLED = False
        try:
            card = main.DrawingCard()
            card.show_page('BL法兰盖.bmp', {}, self.row)
            self.assertFalse(card._vector)
            self.assertFalse(card.pic.pixmap().isNull())
            card.deleteLater()
        finally:
            drawing_card.FLANGE_VECTOR_ENABLED = old


if __name__ == '__main__':
    unittest.main()
