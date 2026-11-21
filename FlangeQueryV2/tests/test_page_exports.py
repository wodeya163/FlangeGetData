# -*- coding: utf-8 -*-
"""用真实 CSV 逐页验证表格列与导出列，需要可导入 PyQt5 的环境。"""

import csv
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
    from PyQt5.QtCore import Qt
except Exception as exc:  # 无 PyQt5 的环境跳过集成测试
    raise unittest.SkipTest('PyQt5 不可用，跳过 GUI 集成测试：%s' % exc)

import main


class PageExportIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.win = main.MainWindow()
        cls.pages = []
        for i in range(cls.win.tree.topLevelItemCount()):
            top = cls.win.tree.topLevelItem(i)
            for j in range(top.childCount()):
                child = top.child(j)
                meta = child.data(0, Qt.UserRole)
                if meta:
                    cls.pages.append((child, meta))

    @classmethod
    def tearDownClass(cls):
        cls.win.deleteLater()
        cls.app.processEvents()

    def test_all_configured_pages_load_and_export_every_column(self):
        self.assertEqual(len(self.pages), sum(len(items) for _, items in main.PAGES))
        checked = 0
        for child, meta in self.pages:
            name, csvf = meta[0], meta[1]
            if len(meta) > 5 and getattr(meta[5], 'kind', '') in ('weight', 'selection'):
                continue
            with self.subTest(page=name, csv=csvf):
                self.win.on_tree(child, 0)
                self.app.processEvents()
                self.assertTrue(self.win.rows, '页面无数据：%s' % name)
                self.assertTrue(self.win.current_cols, '页面无导出列：%s' % name)

                expected = [c for c in self.win.head if not c.startswith('_')]
                self.assertEqual(set(expected) - set(self.win.current_cols), set(),
                                 '页面列未进入表格导出：%s' % name)

                self.win.table.selectRow(0)
                self.app.processEvents()
                self.assertIsNotNone(self.win.cur_row, '选中首行失败：%s' % name)
                self.assertTrue(
                    any(str(v).strip() not in ('', '-')
                        for v in self.win.cur_row.values()),
                    '首行没有可用数据：%s' % name)
                if 'DN' in self.win.head:
                    self.assertIsNotNone(self.win.cur_row.get('DN'),
                                         '首行缺少 DN：%s' % name)

                with tempfile.TemporaryDirectory() as tmp:
                    path = os.path.join(tmp, csvf)
                    main.write_csv(path, [self.win.cur_row],
                                   self.win.current_cols)
                    with open(path, encoding='utf-8-sig', newline='') as fh:
                        header = next(csv.reader(fh))
                    self.assertEqual(header, self.win.current_cols)
                checked += 1
        expected = sum(1 for _, meta in self.pages
                       if not (len(meta) > 5 and getattr(meta[5], 'kind', '') in ('weight', 'selection')))
        self.assertEqual(checked, expected)

    def test_print_preview_renders_flange_and_bellows_to_pdf(self):
        page_map = {meta[1]: child for child, meta in self.pages}
        for csvf in ('HGT20592_带颈对焊.csv', 'U_bellows.csv'):
            with self.subTest(csv=csvf), tempfile.TemporaryDirectory() as tmp:
                self.win.on_tree(page_map[csvf], 0)
                self.win.table.selectRow(0)
                self.app.processEvents()
                self.assertIsNotNone(self.win.cur_row)

                path = os.path.join(tmp, 'preview.pdf')
                printer = main.QPrinter(main.QPrinter.HighResolution)
                printer.setOutputFormat(main.QPrinter.PdfFormat)
                printer.setOutputFileName(path)
                self.win._render_print_page(printer)
                self.assertTrue(os.path.isfile(path))
                with open(path, 'rb') as fh:
                    self.assertEqual(fh.read(4), b'%PDF')


if __name__ == '__main__':
    unittest.main()
