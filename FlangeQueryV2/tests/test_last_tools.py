# -*- coding: utf-8 -*-
"""轴承/齿轮/弹簧核心测试。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.bearing import check  # noqa: E402
from core.bearing_guide import type_guide  # noqa: E402
from core.bearing_variants import variant_guide  # noqa: E402
from core.bolt_calc import calculate_screw_joint  # noqa: E402
from core.gear import contact_ratio, gear_pair  # noqa: E402
from core.spring import compression_spring  # noqa: E402


class LastToolsTest(unittest.TestCase):
    def test_bearing(self):
        res = check('6205', 2.0, 0.5, 1500, 20000)
        self.assertGreater(res['L10h'], 0)
        self.assertGreater(res['S0'], 0)
        self.assertIn('pass', res)

    def test_bearing_guide(self):
        ranked = type_guide('heavy', 'radial_main', 'medium', False,
                            'free', True)
        self.assertEqual(len(ranked), 5)
        self.assertGreater(ranked[0][1], ranked[-1][1])

    def test_bearing_variants(self):
        v = variant_guide('6205')
        self.assertEqual(len(v['seals']), 3)
        self.assertEqual(len(v['clearances']), 3)
        self.assertTrue(v['examples'])

    def test_screw_joint(self):
        r = calculate_screw_joint('M12', '8.8', 'Q235', 8, 1000, 2000,
                                  0, 1, 20, None)
        self.assertGreater(r.preload, 0)
        self.assertGreater(r.thread_stripping_force, 0)
        self.assertGreater(r.safety_factor, 0)

    def test_gear(self):
        res = gear_pair(2, 20, 40)
        self.assertAlmostEqual(res['d1'], 40)
        self.assertAlmostEqual(res['d2'], 80)
        self.assertAlmostEqual(res['a'], 60)
        self.assertGreater(contact_ratio(res), 1)

    def test_spring(self):
        res = compression_spring(3, 20, 10, 79000, 100)
        self.assertGreater(res['rate'], 0)
        self.assertGreater(res['deflection'], 0)
        self.assertGreater(res['stress'], 0)


if __name__ == '__main__':
    unittest.main()
