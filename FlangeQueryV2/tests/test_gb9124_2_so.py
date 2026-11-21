# -*- coding: utf-8 -*-
"""GB/T 9124.2 SO Class150–1500 数据页测试。"""

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
    raise unittest.SkipTest('PyQt5 不可用，跳过 SO 数据测试：%s' % exc)

CSV = 'GBT9124_2_带颈平焊.csv'


class GbSoDataTest(unittest.TestCase):
    def load(self):
        return main.load_csv(os.path.join(ROOT, 'Data', CSV))

    def test_rows_and_values(self):
        _head, rows = self.load()
        self.assertEqual(len(rows), 86)
        self.assertEqual({r['Class'] for r in rows},
                         {'150', '300', '600', '900', '1500'})
        data = {(r['Class'], r['DN']): r for r in rows}
        self.assertEqual(data[('150', '50')]['H'], '24')
        self.assertEqual(data[('300', '50')]['H'], '32')
        self.assertEqual(data[('600', '600')]['H'], '140')
        self.assertEqual(data[('900', '600')]['H'], '203')
        self.assertEqual(data[('1500', '65')]['H'], '64')

    def test_review_and_page(self):
        info = main.review_for(CSV, 'GB/T 9124.2-2019（Class 系列·美洲体系）')
        self.assertEqual(info['status'], 'partial')
        self.assertIn('表25–29', info['source'])
        pages = [(name, csvf) for _g, items in main.PAGES
                 for name, csvf, _t, _l in items]
        self.assertIn(('SO 带颈平焊（GB/T 真值 Class150–1500）', CSV), pages)


if __name__ == '__main__':
    unittest.main()
