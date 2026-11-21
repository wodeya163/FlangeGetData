# -*- coding: utf-8 -*-
"""螺栓拧紧力矩核心测试。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.torque import grades, scenario, sizes, torque  # noqa: E402


class TorqueTest(unittest.TestCase):
    def test_hex_table(self):
        self.assertIn('M10', sizes('hex'))
        self.assertIn('8.8', grades('hex', 'M10'))
        self.assertEqual(torque('hex', 'M10', '8.8'), (41, 48.2, 55.5))

    def test_socket_and_scenario(self):
        self.assertIn('M10', sizes('socket'))
        self.assertEqual(torque('socket', 'M10', '10.9'), (60.2, 70.9, 81.5))
        res = scenario((10, 20, 30), '一般连接')
        self.assertEqual(res[:3], (6.0, 15.0, 27.0))

    def test_missing(self):
        self.assertIsNone(torque('hex', 'M10', '不存在'))


if __name__ == '__main__':
    unittest.main()
