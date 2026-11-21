# -*- coding: utf-8 -*-
"""公差截图 OCR 解析测试。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.tolerance_ocr import ToleranceOCRController, parse_fits  # noqa: E402


class ToleranceOCRTest(unittest.TestCase):
    def test_parse_fit(self):
        fits = parse_fits('φ30 H7/g6')
        self.assertEqual(fits[0]['size'], 30.0)
        self.assertEqual(fits[0]['hole'], 'H7')
        self.assertEqual(fits[0]['shaft'], 'g6')

    def test_repair_ocr_code(self):
        self.assertEqual(
            ToleranceOCRController._repair('gd6', {'g6', 'h6'}), 'g6')
        self.assertEqual(
            ToleranceOCRController._repair('H7', {'H7'}), 'H7')


if __name__ == '__main__':
    unittest.main()
