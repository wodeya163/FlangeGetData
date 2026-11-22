# -*- coding: utf-8 -*-
"""GB/T 9124.1 PDF 转录数据页测试。"""

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
    raise unittest.SkipTest('PyQt5 不可用，跳过 GB/T 数据测试：%s' % exc)

CSV = 'GBT9124_1_带颈对焊.csv'


class Gb9124DataTest(unittest.TestCase):
    def load(self):
        return main.load_csv(os.path.join(ROOT, 'Data', CSV))

    def test_row_count_and_pn(self):
        _head, rows = self.load()
        self.assertEqual(len(rows), 209)
        self.assertEqual({r['PN'] for r in rows},
                         {'2.5', '6', '10', '16', '25', '40', '63',
                          '100', '160', '250', '320', '400'})

    def test_pdf_values_not_hg_alias(self):
        _head, rows = self.load()
        data = {(r['PN'], r['DN']): r for r in rows}
        self.assertEqual(data[('6', '50')]['D'], '140')
        self.assertEqual(data[('6', '50')]['H'], '38')
        self.assertEqual(data[('25', '50')]['C'], '20')
        self.assertEqual(data[('100', '50')]['D'], '195')
        self.assertEqual(data[('160', '50')]['C'], '30')
        self.assertEqual(data[('10', '10')]['S_min'], '2.0')
        self.assertEqual(data[('2.5', '10')]['C'], '12')
        self.assertEqual(data[('2.5', '10')]['H'], '28')
        self.assertEqual(data[('250', '50')]['D'], '200')
        self.assertEqual(data[('250', '50')]['C'], '38')
        self.assertEqual(data[('320', '250')]['D'], '640')
        self.assertEqual(data[('400', '200')]['D'], '585')

    def test_review_status_and_source(self):
        info = main.review_for(CSV, 'GB/T 9124.1-2019（PN 系列·欧洲体系）')
        self.assertEqual(info['status'], 'verified')
        self.assertIn('表27–38', info['source'])
        note = main.source_note('GB/T 9124.1-2019（PN 系列·欧洲体系）', CSV)
        self.assertIn('PN2.5–400', note)

    def test_n_series_ii_matches_pdf(self):
        """2026-11-22 逐项复核：大口径 N 系列Ⅱ与系列Ⅰ不同，不得再填同值。"""
        # 直接从 CSV 读取关键复核点（PDF 表27/表30/表32 实测值）
        import csv
        csv_path = os.path.join(ROOT, 'Data', CSV)
        rows = {}
        with open(csv_path, encoding='utf-8-sig', newline='') as fh:
            for r in csv.DictReader(fh):
                rows[(r['PN'], r['DN'])] = r
        self.assertEqual(rows[('2.5', '350')]['N_A'], '385')
        self.assertEqual(rows[('2.5', '350')]['N_B'], '390')
        self.assertEqual(rows[('10', '600')]['N_A'], '642')
        self.assertEqual(rows[('10', '600')]['N_B'], '650')
        self.assertEqual(rows[('40', '600')]['N_A'], '666')
        self.assertEqual(rows[('40', '600')]['N_B'], '686')

    def test_page_is_registered(self):
        pages = [(name, csvf) for _g, items in main.PAGES
                 for name, csvf, _t, _l in items]
        self.assertIn(('WN 带颈对焊（GB/T 真值 PN2.5–400）', CSV), pages)


if __name__ == '__main__':
    unittest.main()
