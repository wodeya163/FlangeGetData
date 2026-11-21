# -*- coding: utf-8 -*-
"""PageSpec 声明式页面测试。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

try:
    import main
except ImportError as exc:
    raise unittest.SkipTest('PyQt5 不可用，跳过 PageSpec 测试：%s' % exc)


class PageSpecTest(unittest.TestCase):
    def test_all_pages_are_specs(self):
        pages = [page for _std, items in main.PAGES for page in items]
        self.assertGreaterEqual(len(pages), 70)
        for page in pages:
            self.assertIsInstance(page, main.PageSpec)
            self.assertTrue(page.name)
            self.assertIsInstance(page.labels, dict)
            if page.kind in ('weight', 'selection'):
                continue
            self.assertTrue(page.csvf.endswith('.csv'))
            self.assertTrue(page.template.endswith('.bmp'))

    def test_tuple_unpacking_still_works(self):
        name, csvf, template, labels = main.PAGES[0][1][0]
        self.assertTrue(name)
        self.assertTrue(csvf.endswith('.csv'))
        self.assertTrue(template.endswith('.bmp'))
        self.assertIsInstance(labels, dict)

    def test_stem(self):
        page = main.PAGES[0][1][0]
        self.assertEqual(page.stem, page.csvf[:-4])


if __name__ == '__main__':
    unittest.main()
