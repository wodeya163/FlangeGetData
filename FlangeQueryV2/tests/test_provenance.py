# -*- coding: utf-8 -*-
"""FIX-10：GB/T 9124 数据来源标注的契约测试。"""

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
    raise unittest.SkipTest('PyQt5 不可用，跳过来源标注测试：%s' % exc)


class ProvenanceTest(unittest.TestCase):
    def test_provenance_keys_match_page_groups(self):
        groups = {name for name, _ in main.PAGES}
        for key in main.PROVENANCE:
            self.assertIn(key, groups)

    def test_gb_pages_source_notes(self):
        note1 = main.source_note('GB/T 9124.1-2019（PN 系列·欧洲体系）')
        note2 = main.source_note('GB/T 9124.2-2019（Class 系列·美洲体系）')
        # 2026-11-22：9124.1 PN 系列 9 类全部按 PDF 真值复核；
        # 9124.2 为扫描件，Class150 代表表目视抽样复核，其余 Class 未逐条核对。
        self.assertIn('GB/T 9124.1-2019', note1)
        self.assertIn('209 行逐项复核', note1)
        self.assertIn('其余 8 类', note1)
        self.assertIn('GB/T 9124.2-2019', note2)
        self.assertIn('目视抽样复核', note2)
        self.assertIn('未逐条核对', note2)

    def test_gb9124_1_family_source_and_status(self):
        note = main.source_note('GB/T 9124.1-2019（PN 系列·欧洲体系）',
                                'GBT9124_1_法兰盖.csv')
        self.assertIn('表8–91', note)
        self.assertIn('公共尺寸按 PDF 重建', note)
        self.assertEqual(main.review_for(
            'GBT9124_1_法兰盖.csv',
            'GB/T 9124.1-2019（PN 系列·欧洲体系）')['status'], 'verified')

    def test_gb9124_2_still_partial(self):
        info = main.review_for(
            'GBT9124_2_带颈对焊.csv',
            'GB/T 9124.2-2019（Class 系列·美洲体系）')
        self.assertEqual(info['status'], 'partial')
        self.assertIn('抽样复核', info['source'])

    def test_hg_pages_have_no_extra_note(self):
        self.assertEqual(main.source_note('HG/T 20592-2009（欧洲体系）'), '')
        self.assertEqual(main.source_note('HG/T 20615-2009（美洲体系）'), '')

    def test_attach_source_does_not_mutate_rows(self):
        rows = [{'DN': '50'}]
        out = main.attach_source(rows, '数据源：HG/T 20592')
        self.assertEqual(out[0]['数据来源'], '数据源：HG/T 20592')
        self.assertNotIn('数据来源', rows[0])
        self.assertEqual(main.attach_source(rows, ''), rows)


if __name__ == '__main__':
    unittest.main()
