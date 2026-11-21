# -*- coding: utf-8 -*-
"""平键选型核心测试。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.key_select import (check, keyway_depth, parallel_key,  # noqa: E402
                             parallel_check_manual, recommend_key_type,
                             select_length, smart,
                             smart_design, spline_check, taper_check,
                             taper_length, woodruff_check, woodruff_options)


class KeySelectTest(unittest.TestCase):
    def test_dimensions(self):
        self.assertEqual(parallel_key(30), {'b': 8, 'h': 7})
        self.assertEqual(keyway_depth(30), {'t1': 4.0, 't2': 3.3})
        self.assertEqual(parallel_key(10), {'b': 3, 'h': 3})

    def test_length_and_strength(self):
        length = select_length(8, 40)
        self.assertGreaterEqual(length, 8)
        self.assertLessEqual(length, 37)
        res = check(30, 100, 40, '钢', '静载荷')
        self.assertEqual(res['b'], 8)
        self.assertEqual(res['h'], 7)
        self.assertEqual(res['L'], length)
        self.assertGreater(res['sigma_p'], 0)
        self.assertGreater(res['tau'], 0)
        self.assertIn('safe', res)

    def test_smart_screenshot_case(self):
        res = smart(30, 50, 32)
        self.assertEqual((res['b'], res['h'], res['L']), (8, 7, 25))
        self.assertEqual(res['t1'], 4.0)

    def test_other_key_types(self):
        self.assertTrue(woodruff_check(30, 50)['safe'])
        self.assertEqual(woodruff_check(30, 50)['tol']['b'], 'h9')
        self.assertEqual(taper_check(30, 50, 40)['tol']['L'], 'h14')
        self.assertTrue(taper_check(30, 50, 40)['safe'])
        self.assertEqual(spline_check(30, 50, 40)['N'], 6)

    def test_key_type_recommendation(self):
        recs = recommend_key_type(30, '静载荷', False, '一般', False)
        self.assertEqual(recs[0]['type'], 'parallel')
        self.assertIn(recs[0]['verdict'], ('suit', 'ok'))
        self.assertEqual(recs[0]['score'], 110)
        self.assertGreaterEqual(recs[0]['score'], recs[-1]['score'])
        heavy = recommend_key_type(60, '冲击', False, '高', True)
        spline = [r for r in heavy if r['type'] == 'spline']
        self.assertTrue(spline)
        self.assertEqual(spline[0]['verdict'], 'suit')

    def test_smart_type_branches(self):
        self.assertEqual(smart_design(30, 50)['type'], 'parallel')
        self.assertEqual(smart_design(30, 50, None, '钢', '静载荷', True)['type'], 'guided')
        self.assertEqual(smart_design(30, 50, None, '钢', '静载荷', False, '一般', True)['type'], 'taper')
        self.assertEqual(smart_design(60, 50)['type'], 'spline')

    def test_manual_parallel(self):
        r = parallel_check_manual(30, 10, 8, 40, 50, '钢', '静载荷', 'A', '正常联结')
        self.assertTrue(r['safe'])
        self.assertEqual(r['key_type'], 'A')
        self.assertEqual(r['tol']['b'], 'h8')
        self.assertEqual(check(30, 50, 32, key_material='40Cr')['allowable_tau'], 70)
        rows = {x['label']: x for x in check(30, 50, 32)['tolerances']}
        self.assertEqual(rows['键宽 b']['code'], 'h8')
        self.assertEqual(rows['轴槽宽']['upper'], 0)
        self.assertEqual(rows['轴槽宽']['lower'], -36)
        self.assertEqual(rows['毂槽宽']['upper'], 18)

    def test_taper_length_and_spline_fit(self):
        self.assertEqual(taper_length(8, 32, '普通A'), 32)
        self.assertGreaterEqual(taper_length(8, 32, '钩头'), 35)
        self.assertEqual(spline_check(30, 50, 40, centering='外径定心')['fit'],
                         'H7/h6')

    def test_woodruff_options(self):
        opts = woodruff_options(30)
        self.assertTrue(opts)
        r = woodruff_check(30, 50, code=opts[0]['code'])
        self.assertEqual(r['code'], opts[0]['code'])

    def test_invalid(self):
        with self.assertRaises(ValueError):
            check(30, 0, 40)
        with self.assertRaises(ValueError):
            select_length(8, 5)


if __name__ == '__main__':
    unittest.main()
