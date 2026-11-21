# -*- coding: utf-8 -*-
"""选型工具页导航与单位换算测试。"""

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

try:
    from PyQt5.QtWidgets import QApplication
    import main
    from ui import selection_page
except ImportError as exc:
    raise unittest.SkipTest('PyQt5 不可用：%s' % exc)


class SelectionPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.win = main.MainWindow()

    @classmethod
    def tearDownClass(cls):
        cls.win.deleteLater()
        cls.app.processEvents()

    def test_navigation_and_unit_convert(self):
        idx = next(i for i, (name, _) in enumerate(main.TABS)
                   if name == '选型工具')
        self.win.on_tab(idx)
        self.app.processEvents()
        top = next(self.win.tree.topLevelItem(i)
                   for i in range(self.win.tree.topLevelItemCount())
                   if self.win.tree.topLevelItem(i).text(0) == '选型工具')
        self.assertEqual(top.childCount(), 8)
        self.win.on_tree(top.child(1), 0)
        self.app.processEvents()
        self.assertIs(self.win.main_stack.currentWidget(),
                      self.win.selection_page)
        page = self.win.selection_page
        self.assertEqual(page.kind, 'unit')
        page.category.setCurrentText('长度')
        page.from_unit.setCurrentText('m (米)')
        page.to_unit.setCurrentText('mm (毫米)')
        page.amount.setValue(1.0)
        result = page.calculate()
        self.assertAlmostEqual(result, 1000.0)

        self.win.on_tree(top.child(3), 0)
        self.app.processEvents()
        self.assertEqual(page.kind, 'tolerance')
        self.assertIsNotNone(page.tolerance_window)

        self.win.on_tree(top.child(4), 0)
        self.app.processEvents()
        self.assertEqual(page.kind, 'key')
        self.assertFalse(page.key_page.isHidden())
        key_res = page.key_page.calculate()
        self.assertIsNotNone(key_res)
        self.assertIn('推荐键型', page.key_page._result_text())
        rows = page.key_page._result_rows()
        page.key_page.library_page._write([])
        page.key_page._save_to_library()
        self.assertEqual(page.key_page.library_page.list.count(), 1)
        record = page.key_page.library_page._records()[0]
        page.key_page._restore_library(record)
        self.assertEqual(page.key_page.tabs.tabText(
            page.key_page.tabs.currentIndex()), '智能选型')
        self.assertIn(('页面', '智能选型'), rows)
        self.assertTrue(any(k == '规格' and v for k, v in rows))
        page.key_page.tabs.setCurrentIndex(2)
        assistant = page.key_page.tabs.currentWidget()
        assistant.calculate()
        self.assertEqual(assistant.trait_table.rowCount(), 5)
        page.key_page.tabs.setCurrentIndex(1)
        page.key_page.d.setValue(30)
        page.key_page.torque.setValue(50)
        page.key_page.hub_edit.clear()
        page.key_page.hub_material.setCurrentText('铸铁')
        page.key_page.load_type.setCurrentText('静载荷')
        page.key_page.axial_move.setCurrentText('否')
        page.key_page.centering.setCurrentText('高')
        page.key_page.axial_force.setCurrentText('否')
        page.key_page.calculate()
        names = [x[1] for x in selection_page.TOOLS]
        self.assertIn('弹簧设计', names)
        self.assertFalse(any(n.endswith('工具') for n in names))
        self.assertIn('总览', [page.key_page.tabs.tabText(i)
                              for i in range(page.key_page.tabs.count())])
        page.key_page._open_detail()
        self.assertEqual(page.key_page.tabs.tabText(
            page.key_page.tabs.currentIndex()), '平键')
        self.assertIn('最近选型', page.key_page.history_label.text())
        self.assertGreaterEqual(page.key_page.history_list.count(), 1)
        page.key_page._clear_history()
        self.assertEqual(page.key_page.history_list.count(), 0)
        self.assertIn('GB/T 1096', page.key_page._help_text())
        with tempfile.TemporaryDirectory() as tmp:
            pdf = os.path.join(tmp, 'key.pdf')
            page.key_page._render_pdf(pdf)
            with open(pdf, 'rb') as fh:
                self.assertEqual(fh.read(4), b'%PDF')
        self.assertGreater(key_res['sigma_p'], 0)

        self.win.on_tree(top.child(5), 0)
        self.app.processEvents()
        self.assertEqual(page.kind, 'bolt')
        self.assertFalse(page.bolt_page.isHidden())
        bolt_res = page.bolt_page.calculate()
        self.assertIsNotNone(bolt_res)
        self.assertGreater(bolt_res.safety_factor, 0)

        self.win.on_tree(top.child(6), 0)
        self.app.processEvents()
        self.assertEqual(page.kind, 'torque')
        self.assertFalse(page.torque_page.isHidden())
        torque_res = page.torque_page.calculate()
        self.assertIsNotNone(torque_res)
        self.assertGreater(torque_res, 0)

        self.win.on_tree(top.child(0), 0)
        self.app.processEvents()
        self.assertEqual(page.kind, 'gear')
        self.assertFalse(page.gear_page.isHidden())
        self.assertEqual(page.gear_page.tabs.count(), 8)
        self.assertIsNotNone(page.gear_page.calculate())

        self.win.on_tree(top.child(2), 0)
        self.app.processEvents()
        self.assertEqual(page.kind, 'spring')
        self.assertFalse(page.spring_page.isHidden())
        self.assertIsNotNone(page.spring_page.calculate())

        self.win.on_tree(top.child(7), 0)
        self.app.processEvents()
        self.assertEqual(page.kind, 'bearing')
        self.assertFalse(page.bearing_page.isHidden())
        self.assertIsNotNone(page.bearing_page.calculate())


if __name__ == '__main__':
    unittest.main()
