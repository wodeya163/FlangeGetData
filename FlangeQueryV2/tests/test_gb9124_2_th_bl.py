# -*- coding: utf-8 -*-
"""GB/T 9124.2 Th/BL Class150 数据页测试。"""

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
    raise unittest.SkipTest('PyQt5 不可用，跳过 Th/BL 测试：%s' % exc)


class GbThBlTest(unittest.TestCase):
    def load(self, name):
        return main.load_csv(os.path.join(ROOT, 'Data', name))

    def test_th(self):
        _h, rows = self.load('GBT9124_2_螺纹.csv')
        self.assertEqual(len(rows), 93)
        self.assertEqual({r['Class'] for r in rows},
                         {'150', '300', '600', '900', '1500', '2500'})
        data = {(r['Class'], r['DN']): r for r in rows}
        self.assertEqual(data[('150', '50')]['C'], '17.5')
        self.assertEqual(data[('300', '50')]['H'], '32')
        self.assertEqual(data[('2500', '65')]['H'], '79')

    def test_bl(self):
        _h, rows = self.load('GBT9124_2_法兰盖.csv')
        self.assertEqual(len(rows), 93)
        data = {(r['Class'], r['DN']): r for r in rows}
        self.assertEqual(data[('150', '50')]['D'], '150')
        self.assertEqual(data[('2500', '65')]['C'], '57.2')
        self.assertNotIn('H', rows[0])


if __name__ == '__main__':
    unittest.main()
