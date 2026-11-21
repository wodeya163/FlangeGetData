# -*- coding: utf-8 -*-
"""HG/T 20592 不锈钢衬里法兰盖 RF 尺寸校验。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import main  # noqa: E402


class LinedBlFaceTest(unittest.TestCase):
    def test_rf_matches_standard_columns(self):
        _head, rows = main.load_csv(
            os.path.join(ROOT, 'Data', 'HGT20592_不锈钢衬里法兰盖.csv'))
        self.assertEqual(len(rows), 75)
        for row in rows:
            self.assertEqual(row.get('密封面'), 'RF')
            self.assertEqual(row.get('RF_d'), row.get('d0'))
            self.assertEqual(row.get('RF_f1'), row.get('t_t'))

    def test_pn6_dn40_reference(self):
        _head, rows = main.load_csv(
            os.path.join(ROOT, 'Data', 'HGT20592_不锈钢衬里法兰盖.csv'))
        row = next(r for r in rows if r['PN'] == '6' and r['DN'] == '40')
        # HG/T 20592-2009 表 8.2.10-1
        self.assertEqual(row['d0'], '80')
        self.assertEqual(row['t_t'], '3')
        self.assertEqual(row['RF_d'], '80')
        self.assertEqual(row['RF_f1'], '3')


if __name__ == '__main__':
    unittest.main()
