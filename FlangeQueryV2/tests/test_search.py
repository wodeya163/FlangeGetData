# -*- coding: utf-8 -*-
"""FIX-15：全库搜索与尺寸反查的单元测试。"""

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
    raise unittest.SkipTest('PyQt5 不可用，跳过搜索测试：%s' % exc)


class QueryParseTest(unittest.TestCase):
    HEAD = ['DN', 'PN', 'Class', 'K', 'D', 'n', 'Th', 'D_o']

    def test_equals_form(self):
        dims, free = main.split_query('K=125 n=4', self.HEAD)
        self.assertEqual(dims, [('K', '125'), ('n', '4')])
        self.assertEqual(free, [])

    def test_prefix_form(self):
        dims, _free = main.split_query('DN50 PN16 Class150', self.HEAD)
        self.assertEqual(dims, [('DN', '50'), ('PN', '16'),
                                ('Class', '150')])

    def test_keyword_stays_free(self):
        dims, free = main.split_query('不锈钢 DN50', self.HEAD)
        self.assertEqual(dims, [('DN', '50')])
        self.assertEqual(free, ['不锈钢'])

    def test_unknown_column_becomes_free(self):
        dims, free = main.split_query('XYZ=1', self.HEAD)
        self.assertEqual(dims, [])
        self.assertEqual(free, ['XYZ=1'])


class SearchTest(unittest.TestCase):
    def test_dimension_search(self):
        results = main.search_all('D=165 K=125', limit=30)
        self.assertTrue(results)
        for _std, _name, _csv, row, _summary in results:
            self.assertEqual(float(row['D']), 165)
            self.assertEqual(float(row['K']), 125)

    def test_keyword_search_hits_page_name(self):
        results = main.search_all('不锈钢', limit=5)
        self.assertEqual(len(results), 5)

    def test_empty_query(self):
        self.assertEqual(main.search_all('', limit=5), [])

    def test_limit_is_respected(self):
        self.assertEqual(len(main.search_all('DN=50', limit=7)), 7)


if __name__ == '__main__':
    unittest.main()
