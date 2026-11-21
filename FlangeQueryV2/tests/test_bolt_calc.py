# -*- coding: utf-8 -*-
"""螺栓连接校核核心测试。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.bolt_calc import calculate_bolt_joint  # noqa: E402


class BoltCalcTest(unittest.TestCase):
    def test_joint(self):
        res = calculate_bolt_joint(
            'M10', '8.8', 'Q235', 8, '喷砂-钢', 1000, 2000, 0,
            4, 1, 20, None)
        self.assertGreater(res.preload, 0)
        self.assertGreater(res.bolt_tension_capacity, 0)
        self.assertGreater(res.safety_factor, 0)
        self.assertIn(res.failure_mode, res.details['safety_factors'])

    def test_moment(self):
        res = calculate_bolt_joint(
            'M12', '8.8', 'Q345', 10, '喷砂-钢', 800, 1500, 5000,
            4, 2, 24, [(0, 0), (40, 0), (0, 40), (40, 40)])
        self.assertGreater(res.safety_factor, 0)

    def test_bad_size(self):
        with self.assertRaises(KeyError):
            calculate_bolt_joint('M999', '8.8', 'Q235', 8, '喷砂-钢',
                                 1000, 2000, 0, 4, 1, 20, None)


if __name__ == '__main__':
    unittest.main()
