# -*- coding: utf-8 -*-
"""行级复核字段与面型缺口清单测试。"""

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.review import annotate_rows, attach_review, attach_source  # noqa: E402


class RowReviewTest(unittest.TestCase):
    def test_file_and_row_review(self):
        rows = [
            {'DN': '50', 'RF_d': '', 'RF_f1': ''},
            {'DN': '80', 'RF_d': '100', 'RF_f1': '2',
             'review_status': 'verified', 'review_source': 'PDF 表 12'},
        ]
        out = annotate_rows(rows, 'HGT20592_带颈对焊.csv',
                            'HG/T 20592-2009')
        self.assertEqual(out[0]['复核状态'], '部分核对')
        self.assertEqual(out[0]['face_status'], 'missing')
        self.assertEqual(out[1]['复核状态'], '已核对')
        self.assertEqual(out[1]['数据来源'], 'PDF 表 12')
        self.assertEqual(out[1]['face_status'], 'complete')
        self.assertIn('复核状态', out[0])
        self.assertIn('数据来源', out[0])
        exported = attach_source(
            attach_review(out, {'label': '部分核对', 'source': '文件级'}),
            '文件级')
        self.assertEqual(exported[1]['复核状态'], '已核对')
        self.assertEqual(exported[1]['数据来源'], 'PDF 表 12')

    def test_face_audit_matches_items(self):
        path = os.path.join(ROOT, 'Data', 'face_audit.json')
        self.assertTrue(os.path.isfile(path), '缺少面型缺口清单')
        with open(path, encoding='utf-8') as fh:
            data = json.load(fh)
        self.assertEqual(data['rf_missing'], len(data['items']))
        self.assertGreater(data['total_rows'], 0)


if __name__ == '__main__':
    unittest.main()
