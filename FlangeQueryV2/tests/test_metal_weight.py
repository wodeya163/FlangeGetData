# -*- coding: utf-8 -*-
"""金属材料重量计算测试（数据移植自 metal-material-calculator）。"""

import math
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.metal_weight import (MATERIALS, SHAPES, calculate)  # noqa: E402


class MetalWeightTest(unittest.TestCase):
    def test_data_coverage(self):
        self.assertEqual(len(SHAPES), 9)
        self.assertEqual(len(MATERIALS), 16)

    def test_plate_and_round_bar(self):
        plate = calculate('plate', 'steel',
                          {'t': 10, 'w': 100, 'l': 1000})
        self.assertAlmostEqual(plate['mass'], 7.85, places=6)
        bar = calculate('round-bar', 'steel', {'d': 50, 'l': 1000})
        self.assertAlmostEqual(
            bar['mass'], math.pi / 4 * 5 ** 2 * 100 * 7.85 / 1000,
            places=6)

    def test_tube_and_wall_validation(self):
        tube = calculate('round-tube', 'aluminum',
                         {'D': 50, 't': 3, 'l': 1000})
        self.assertGreater(tube['mass'], 0)
        with self.assertRaises(ValueError):
            calculate('round-tube', 'steel', {'D': 50, 't': 25, 'l': 1000})

    def test_channel_material_scaling(self):
        steel = calculate('channel', 'steel', {'spec': '10#', 'l': 1000})
        s304 = calculate('channel', 's304', {'spec': '10#', 'l': 1000})
        self.assertAlmostEqual(steel['mass'], 10.007, places=3)
        self.assertGreater(s304['mass'], steel['mass'])

    def test_custom_density_and_quantity(self):
        res = calculate('square-bar', 'custom',
                        {'a': 50, 'l': 1000}, quantity=2,
                        custom_density=2.7)
        self.assertEqual(res['quantity'], 2)
        self.assertAlmostEqual(res['total'], res['mass'] * 2, places=9)


if __name__ == '__main__':
    unittest.main()
