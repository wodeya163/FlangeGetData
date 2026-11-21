# -*- coding: utf-8 -*-
"""FIX-12：未校准页面不再叠加错位数值标注。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

try:
    import main
except ImportError as exc:
    raise unittest.SkipTest('PyQt5 不可用，跳过标注策略测试：%s' % exc)


class LabelPolicyTest(unittest.TestCase):
    def test_wn_labels_are_kept(self):
        self.assertTrue(main.WN_LABELS)
        self.assertIn('D', main.WN_LABELS)

    def test_generic_labels_are_hidden(self):
        self.assertEqual(main.GENERIC_LABELS, {})

    def test_pages_using_generic_labels_have_no_callouts(self):
        hits = 0
        for _group, items in main.PAGES:
            for _name, _csvf, _tpl, labels in items:
                if labels is main.GENERIC_LABELS:
                    hits += 1
                    self.assertEqual(labels, {})
        self.assertGreater(hits, 0)


if __name__ == '__main__':
    unittest.main()
