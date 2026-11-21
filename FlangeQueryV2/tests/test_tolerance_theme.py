# -*- coding: utf-8 -*-
"""公差查询主题与调色板测试。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from vendor.tolerance.ui.theme import get_palette, load_theme_name  # noqa: E402


class ToleranceThemeTest(unittest.TestCase):
    def test_forced_light_theme(self):
        self.assertEqual(load_theme_name(), 'FlangeQuery')
        p = get_palette()
        self.assertEqual(p['BG'].lower(), '#f5f8fb')
        self.assertEqual(p['CARD'].lower(), '#ffffff')
        self.assertEqual(p['TEXT'].lower(), '#17202a')
        self.assertEqual(p['ACCENT'].lower(), '#1f4e79')


if __name__ == '__main__':
    unittest.main()
