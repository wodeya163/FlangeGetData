# -*- coding: utf-8 -*-
"""重量计算核心测试。"""

import math
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.weight import (angle_tee_weight, bend_tee_weight, elbow_weight,
                         large_radius_elbow_weight, pipe_weight,
                         tee_weight)  # noqa: E402


class WeightTest(unittest.TestCase):
    def test_pipe(self):
        res = pipe_weight(100, 10, 1.0, 1000)
        area = math.pi * 90 * 10
        self.assertAlmostEqual(res['area'], area, places=6)
        self.assertAlmostEqual(res['mass'], area * 1000 / 1e9 * 1000,
                               places=6)

    def test_elbow(self):
        res = elbow_weight(100, 10, 150, 90, 1000)
        area = math.pi * 90 * 10
        self.assertAlmostEqual(res['mass'],
                               area * 150 * math.pi / 2 / 1e9 * 1000,
                               places=6)

    def test_large_radius_elbow(self):
        res = large_radius_elbow_weight(100, 10, 300, 90, 100, 100, 1000)
        area = math.pi * 90 * 10
        length = 300 * math.pi / 2 + 200
        self.assertAlmostEqual(res['mass'],
                               area * length / 1e9 * 1000, places=6)
        self.assertGreater(res['mass'],
                           elbow_weight(100, 10, 150, 90, 1000)['mass'])

    def test_tee_types_and_price(self):
        std = tee_weight(100, 80, 10, 200, 100, 1000, 6.5)
        angle = angle_tee_weight(100, 80, 10, 200, 100, 45, 1000, 6.5)
        bend = bend_tee_weight(100, 80, 10, 200, 100, 90, 90, 1000, 6.5)
        self.assertAlmostEqual(std['price'], std['mass'] * 6.5, places=6)
        self.assertGreater(angle['mass'], std['mass'])
        self.assertGreater(bend['mass'], std['mass'])
        self.assertGreater(bend['price'], 0)

    def test_tee_and_invalid(self):
        res = tee_weight(100, 80, 10, 200, 100, 1000)
        self.assertGreater(res['mass'], 0)
        with self.assertRaises(ValueError):
            pipe_weight(0, 1, 1, 1000)
        with self.assertRaises(ValueError):
            pipe_weight(20, 10, 1, 1000)


if __name__ == '__main__':
    unittest.main()
