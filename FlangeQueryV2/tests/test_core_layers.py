# -*- coding: utf-8 -*-
"""核心层直接测试：不依赖 Qt Widgets。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.page_spec import PageSpec  # noqa: E402
from core.review import review_for, source_note, STANDARDS_COVERAGE  # noqa: E402


class CoreLayerTest(unittest.TestCase):
    def test_review_module(self):
        info = review_for('GBT9124_2_带颈对焊.csv',
                          'GB/T 9124.2-2019（Class 系列·美洲体系）')
        self.assertEqual(info['status'], 'partial')
        self.assertIn('表19–24', info['source'])
        self.assertTrue(source_note('GB/T 9124.1-2019（PN 系列·欧洲体系）',
                                    'GBT9124_1_带颈对焊.csv'))

    def test_coverage_matrix(self):
        self.assertGreaterEqual(len(STANDARDS_COVERAGE), 20)

    def test_page_spec_model(self):
        page = PageSpec('WN', 'x.csv', 'x.bmp', {})
        self.assertEqual(page.stem, 'x')
        self.assertEqual(tuple(page), ('WN', 'x.csv', 'x.bmp', {}))


if __name__ == '__main__':
    unittest.main()
