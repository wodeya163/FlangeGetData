# -*- coding: utf-8 -*-
"""重量计算页面导航与计算测试。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

try:
    from PyQt5.QtWidgets import QApplication
    import main
except ImportError as exc:
    raise unittest.SkipTest('PyQt5 不可用：%s' % exc)


class WeightPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.win = main.MainWindow()

    @classmethod
    def tearDownClass(cls):
        cls.win.deleteLater()
        cls.app.processEvents()

    def test_navigation_and_calculate(self):
        idx = next(i for i, (name, _) in enumerate(main.TABS)
                   if name == '重量计算')
        self.win.on_tab(idx)
        self.app.processEvents()
        top = next(self.win.tree.topLevelItem(i)
                   for i in range(self.win.tree.topLevelItemCount())
                   if self.win.tree.topLevelItem(i).text(0) == '重量计算')
        self.assertEqual(top.childCount(), 4)
        child = top.child(0)
        self.win.on_tree(child, 0)
        self.app.processEvents()
        self.assertIs(self.win.main_stack.currentWidget(),
                      self.win.weight_page)
        self.assertEqual(self.win.weight_page.kind, 'pipe')
        self.win.weight_page.unit_price.setValue(5.0)
        res = self.win.weight_page.calculate()
        self.assertIsNotNone(res)
        self.assertGreater(res['mass'], 0)
        self.assertNotEqual(self.win.weight_page.mass.text(), '—')
        self.assertGreater(res['price'], 0)
        self.assertIn('采购价格', self.win.weight_page.price_result.text())
        self.assertIsNotNone(self.win.weight_page.preview.pixmap())
        elbow = top.child(1)
        self.win.on_tree(elbow, 0)
        self.app.processEvents()
        self.assertEqual(self.win.weight_page.kind, 'elbow')
        res = self.win.weight_page.calculate()
        self.assertIsNotNone(res)
        self.assertGreater(res['mass'], 0)
        self.assertGreater(res['price'], 0)
        self.assertIsNotNone(self.win.weight_page.preview.pixmap())
        page = self.win.weight_page
        self.assertEqual([page.elbow_tabs.tabText(i)
                          for i in range(page.elbow_tabs.count())],
                         ['标准弯头', '大曲率弯头'])
        std_mass = res['mass']
        page.elbow_tabs.setCurrentIndex(1)
        self.app.processEvents()
        self.assertGreater(page.large_material.count(), 1)
        page.large_material.setCurrentIndex(1)
        self.assertIn('7930', page.large_density.text())
        large = page.calculate()
        self.assertIsNotNone(large)
        self.assertGreater(large['mass'], std_mass)
        self.assertIsNotNone(page.preview.pixmap())
        tee = top.child(2)
        self.win.on_tree(tee, 0)
        self.app.processEvents()
        tp = self.win.weight_page
        self.assertEqual([tp.tee_tabs.tabText(i)
                          for i in range(tp.tee_tabs.count())],
                         ['标准三通', '斜三通', '弯三通'])
        tp.tee_price.setValue(6.5)
        std = tp.calculate()
        self.assertGreater(std['price'], 0)
        self.assertIn('采购价格', tp.price_result.text())
        self.assertIsNotNone(tp.preview.pixmap())
        tp.tee_tabs.setCurrentIndex(1)
        self.app.processEvents()
        self.assertGreater(tp.calculate()['mass'], 0)
        self.assertIsNotNone(tp.preview.pixmap())
        tp.tee_tabs.setCurrentIndex(2)
        self.app.processEvents()
        self.assertGreater(tp.calculate()['mass'], 0)
        self.assertIsNotNone(tp.preview.pixmap())
        metal = top.child(3)
        self.win.on_tree(metal, 0)
        self.app.processEvents()
        mp = self.win.metal_weight_page
        self.assertIs(self.win.main_stack.currentWidget(), mp)
        self.assertEqual(mp.shape.currentText(), '板材')
        mp.price.setValue(5.0)
        self.assertGreater(mp.calculate()['mass'], 0)
        self.assertIn('采购价格', mp.price_line.text())
        mp.shape.setCurrentIndex(4)
        self.app.processEvents()
        self.assertEqual(mp.shape.currentText(), '圆管')
        self.assertGreater(mp.calculate()['mass'], 0)


if __name__ == '__main__':
    unittest.main()
