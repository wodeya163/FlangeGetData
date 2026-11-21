# -*- coding: utf-8 -*-
"""3.1 数据治理：复核状态、覆盖矩阵与导出元数据测试。"""

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
    raise unittest.SkipTest('PyQt5 不可用，跳过来源状态测试：%s' % exc)


class ReviewStatusTest(unittest.TestCase):
    def test_verified_source(self):
        info = main.review_for('GB17395_普通钢管.csv')
        self.assertEqual(info['status'], 'verified')
        self.assertIn('GB/T 17395', info['source'])

    def test_partial_and_inferred_sources(self):
        self.assertEqual(main.review_for('HGT20592_带颈对焊.csv')['status'],
                         'partial')
        self.assertEqual(main.review_for('HGT20610.csv')['status'],
                         'inferred')
        self.assertEqual(main.review_for('mfm_RF.csv')['status'],
                         'descriptive')

    def test_gb_alias_is_marked(self):
        info = main.review_for('HGT20592_带颈对焊.csv',
                               'GB/T 9124.1-2019（PN 系列·欧洲体系）')
        self.assertEqual(info['status'], 'alias')
        self.assertIn('20592', info['source'])

    def test_unknown_source(self):
        info = main.review_for('不存在.csv')
        self.assertEqual(info['status'], 'unknown')

    def test_coverage_matrix_has_gaps(self):
        self.assertGreaterEqual(len(main.STANDARDS_COVERAGE), 20)
        numbers = {row[0] for row in main.STANDARDS_COVERAGE}
        self.assertIn('GB/T 9124.1-2019', numbers)
        self.assertIn('HG/T 20627-2009', numbers)
        statuses = {row[3] for row in main.STANDARDS_COVERAGE}
        self.assertIn('missing', statuses)
        self.assertIn('alias', statuses)

    def test_attach_review_does_not_mutate_rows(self):
        rows = [{'DN': '50'}]
        info = main.review_for('HGT20592_带颈对焊.csv')
        out = main.attach_review(rows, info)
        self.assertEqual(out[0]['复核状态'], '部分核对')
        self.assertIn('原程序 CSV', out[0]['数据来源'])
        self.assertNotIn('复核状态', rows[0])

    def test_attach_source_always_returns_copy(self):
        rows = [{'DN': '50'}]
        out = main.attach_source(rows, '')
        self.assertEqual(out, rows)
        self.assertIsNot(out[0], rows[0])


if __name__ == '__main__':
    unittest.main()
