# -*- coding: utf-8 -*-
"""FIX-09：历史列名归一与伪列清理的契约测试。"""

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
    raise unittest.SkipTest('PyQt5 不可用，跳过列名测试：%s' % exc)

DATA_DIR = os.path.join(ROOT, 'Data')


class ColumnNormalizationTest(unittest.TestCase):
    def load(self, name):
        return main.load_csv(os.path.join(DATA_DIR, name))

    def test_mass_alias_kg_to_m_kg(self):
        head, rows = self.load('HGT20615_螺纹.csv')
        self.assertIn('m_kg', head)
        self.assertNotIn('kg', head)
        self.assertTrue(rows[0]['m_kg'])

    def test_rj_case_alias(self):
        head, _ = self.load('HGT20615_长高颈.csv')
        self.assertIn('RJ_r', head)
        self.assertNotIn('RJ_R', head)
        head, _ = self.load('HGT20592_法兰盖.csv')
        self.assertIn('RJ_r', head)
        self.assertNotIn('RJ_R', head)

    def test_duplicate_suffix_column_removed(self):
        head, _ = self.load('HGT20615_承插焊.csv')
        self.assertIn('RF_d', head)
        self.assertNotIn('RF_d.1', head)

    def test_pn2_mapped_to_class(self):
        head, rows = self.load('HGT20615_法兰盖.csv')
        self.assertIn('Class', head)
        self.assertNotIn('PN2', head)
        self.assertEqual(rows[0]['Class'], '150')

    def test_pseudo_pn_removed_for_class_series(self):
        head, _ = self.load('HGT20615_带颈对焊.csv')
        self.assertIn('Class', head)
        self.assertNotIn('PN', head)
        head, _ = self.load('HGT20623_带颈对焊A系列.csv')
        self.assertIn('Class', head)
        self.assertNotIn('PN', head)

    def test_hg_pn_series_keeps_pn(self):
        head, _ = self.load('HGT20592_带颈对焊.csv')
        self.assertIn('PN', head)
        self.assertNotIn('Class', head)

    def test_extra_mass_columns_stay_available(self):
        head, rows = self.load('HGT20592_对焊环松套.csv')
        self.assertIn('PJ_m_kg', head)
        self.assertIn('SE_m_kg', head)
        self.assertTrue(rows[0]['PJ_m_kg'])

    def test_class_dn_units_are_swapped(self):
        head, rows = self.load('HGT20615_带颈对焊.csv')
        self.assertIn('DN', head)
        self.assertIn('DN2', head)
        self.assertEqual(rows[0]['DN'], '15')
        self.assertEqual(rows[0]['DN2'], '1/2"')

    def test_no_class_csv_contains_pseudo_pn(self):
        names = [n for n in sorted(os.listdir(DATA_DIR))
                 if n.startswith(('HGT20615_', 'HGT20623_'))
                 and n.lower().endswith('.csv')]
        self.assertEqual(len(names), 12)
        for name in names:
            with self.subTest(csv=name):
                head, rows = self.load(name)
                self.assertIn('Class', head)
                self.assertNotIn('PN', head)
                for r in rows:
                    self.assertFalse(str(r.get('PN', '')).lower().startswith('class'))


if __name__ == '__main__':
    unittest.main()
