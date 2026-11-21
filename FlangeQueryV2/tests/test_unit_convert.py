# -*- coding: utf-8 -*-
"""单位换算核心测试。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.unit_convert import (category_names, convert, formula,
                               unit_labels, units)  # noqa: E402


class UnitConvertTest(unittest.TestCase):
    def test_length_and_area(self):
        self.assertAlmostEqual(convert(1, '长度', 'm', 'mm'), 1000)
        self.assertAlmostEqual(convert(1000, '长度', 'mm', 'm'), 1)
        self.assertAlmostEqual(convert(1, '面积', 'm²', 'mm²'), 1e6)

    def test_temperature(self):
        self.assertAlmostEqual(convert(0, '温度', '°C', '°F'), 32)
        self.assertAlmostEqual(convert(212, '温度', '°F', '°C'), 100)
        self.assertAlmostEqual(convert(0, '温度', '°C', 'K'), 273.15)

    def test_units_and_formula(self):
        self.assertEqual(units('温度'), ('°C', '°F', 'K'))
        self.assertIn('1 m = 1000 mm', formula('长度', 'm', 'mm'))
        self.assertEqual(len(category_names()), 21)
        self.assertIn('mm (毫米)', unit_labels('长度'))
        with self.assertRaises(ValueError):
            convert(1, '长度', 'm', 'kg')

    def test_dms_and_hardness(self):
        self.assertAlmostEqual(convert(1, '角度', '°', '′'), 60)
        self.assertAlmostEqual(convert(30, '硬度', 'HRC', 'HBW'), 283)
        self.assertIn('度分秒', formula('角度', '度分秒', '°'))


if __name__ == '__main__':
    unittest.main()
