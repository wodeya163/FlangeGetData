# -*- coding: utf-8 -*-
"""齿轮工具计算回归。"""

import math
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.gear import (bevel_gear, helical_gear, nearest_module,
                       pair_center_distance, spur_gear)
from core.gear_m_value import calc_m_value_simple, solve_x_from_m_value
from core.gear_stp import _tooth_points
from core.gear_strength import calc_zhang_xuemeng
from core.gear_tooth_thickness import calc_k_from_z, convert_tooth_thickness


class GearToolsTest(unittest.TestCase):
    def test_spur_geometry(self):
        r = spur_gear(3, 20)
        self.assertAlmostEqual(r['d'], 60.0)
        self.assertAlmostEqual(r['da'], 66.0)
        self.assertAlmostEqual(r['df'], 52.5)
        self.assertAlmostEqual(r['p'], math.pi * 3)

    def test_helical_geometry(self):
        r = helical_gear(3, 20, 15)
        self.assertGreater(r['mt'], 3)
        self.assertAlmostEqual(r['d'], r['mt'] * 20)
        self.assertGreater(r['zv'], 20)

    def test_bevel_geometry(self):
        r = bevel_gear(20, 30, 3, 16)
        self.assertAlmostEqual(r['delta1'] + r['delta2'], 90)
        self.assertGreater(r['R'], 0)
        self.assertGreater(r['ratio'], 1)

    def test_pair_and_module(self):
        a, ap, ratio = pair_center_distance('spur', 3, 20, 40)
        self.assertAlmostEqual(a, 90)
        self.assertAlmostEqual(ap, 90)
        self.assertAlmostEqual(ratio, 2)
        self.assertEqual(nearest_module(2.9), 3)

    def test_m_value_roundtrip(self):
        m = calc_m_value_simple(20, 3, 20, 0, 5)
        self.assertGreater(m, 60)
        x, m2 = solve_x_from_m_value(20, 3, 20, 5, m)
        self.assertIsNotNone(x)
        self.assertAlmostEqual(m2, m, places=3)

    def test_tooth_thickness(self):
        k = calc_k_from_z(20, 20, 0)
        r = convert_tooth_thickness(20, 3, 20, 0, 5, k=k)
        self.assertEqual(r['k'], k)
        self.assertGreater(r['W'], 20)
        self.assertGreater(r['M'], 60)

    def test_stp_profile(self):
        pts = _tooth_points(3, 20)
        self.assertEqual(len(pts), 20 * 8)
        radii = [math.hypot(x, y) for x, y in pts]
        self.assertGreater(max(radii), 30)
        self.assertLess(min(radii), 30)

    def test_strength(self):
        r = calc_zhang_xuemeng(10, 20, 40, 3, 20, 0, 20, 0, 0,
                               '45钢_调质', '45钢_正火')
        self.assertIn('contact', r)
        self.assertIn('bending1', r)
        self.assertGreater(r['contact']['sigma_H'], 0)


if __name__ == '__main__':
    unittest.main()
