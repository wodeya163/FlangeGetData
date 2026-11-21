# -*- coding: utf-8 -*-
"""GB/T 9124.2 Class150–2500 对焊数据页测试。"""

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
    raise unittest.SkipTest('PyQt5 不可用，跳过 GB/T 9124.2 数据测试：%s' % exc)

CSV = 'GBT9124_2_带颈对焊.csv'


class Gb9124TwoDataTest(unittest.TestCase):
    def load(self):
        return main.load_csv(os.path.join(ROOT, 'Data', CSV))

    def test_row_count_and_class(self):
        _head, rows = self.load()
        self.assertEqual(len(rows), 112)
        self.assertEqual({r['Class'] for r in rows},
                         {'150', '300', '600', '900', '1500', '2500'})
        self.assertEqual(rows[0]['DN'], '15')
        self.assertEqual(rows[-1]['DN'], '300')

    def test_pdf_values(self):
        _head, rows = self.load()
        data = {(r['Class'], r['DN']): r for r in rows}
        self.assertEqual(data[('300', '50')]['D'], '165')
        self.assertEqual(data[('300', '50')]['C'], '20.7')
        self.assertEqual(data[('600', '600')]['D'], '940')
        self.assertEqual(data[('900', '600')]['H'], '292')
        self.assertEqual(data[('1500', '600')]['C'], '203.2')
        self.assertEqual(data[('2500', '300')]['N_A'], '441')

    def test_wall_and_bore_fields(self):
        _head, rows = self.load()
        row = next(r for r in rows
                   if r['Class'] == '150' and r['DN'] == '50')
        self.assertEqual(row['S'], '3.91')
        self.assertEqual(row['d_bore'], '52.48')

    def test_review_status_and_source(self):
        info = main.review_for(CSV, 'GB/T 9124.2-2019（Class 系列·美洲体系）')
        self.assertEqual(info['status'], 'partial')
        self.assertIn('表19–24', info['source'])
        note = main.source_note('GB/T 9124.2-2019（Class 系列·美洲体系）', CSV)
        self.assertIn('Class150–2500', note)

    def test_page_is_registered(self):
        pages = [(name, csvf) for _g, items in main.PAGES
                 for name, csvf, _t, _l in items]
        self.assertIn(('WN 带颈对焊（GB/T 真值 Class150–2500）', CSV), pages)


if __name__ == '__main__':
    unittest.main()
