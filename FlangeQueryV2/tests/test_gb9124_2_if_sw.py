# -*- coding: utf-8 -*-
"""GB/T 9124.2 IF/SW Class150 数据页测试。"""

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
    raise unittest.SkipTest('PyQt5 不可用，跳过 IF/SW 测试：%s' % exc)


class GbIfSwTest(unittest.TestCase):
    def load(self, name):
        return main.load_csv(os.path.join(ROOT, 'Data', name))

    def test_if_class150(self):
        _h, rows = self.load('GBT9124_2_整体.csv')
        self.assertEqual(len(rows), 112)
        self.assertEqual({r['Class'] for r in rows},
                         {'150', '300', '600', '900', '1500', '2500'})
        data = {(r['Class'], r['DN']): r for r in rows}
        self.assertEqual(data[('150', '50')]['C'], '14.3')
        self.assertEqual(data[('300', '50')]['C'], '20.7')
        self.assertEqual(data[('600', '600')]['N_A'], '718')

    def test_sw_class150(self):
        _h, rows = self.load('GBT9124_2_承插焊.csv')
        self.assertEqual(len(rows), 38)
        self.assertEqual({r['Class'] for r in rows},
                         {'150', '300', '600', '900', '1500'})
        data = {(r['Class'], r['DN']): r for r in rows}
        self.assertEqual(data[('150', '50')]['C'], '17.5')
        self.assertEqual(data[('300', '80')]['H'], '41')
        self.assertEqual(data[('1500', '65')]['H'], '64')

    def test_pages_registered(self):
        pages = [(name, csvf) for _g, items in main.PAGES
                 for name, csvf, _t, _l in items]
        self.assertIn(('IF 整体法兰（GB/T 真值 Class150–2500）',
                       'GBT9124_2_整体.csv'), pages)
        self.assertIn(('SW 承插焊（GB/T 真值 Class150–1500）',
                       'GBT9124_2_承插焊.csv'), pages)


if __name__ == '__main__':
    unittest.main()
