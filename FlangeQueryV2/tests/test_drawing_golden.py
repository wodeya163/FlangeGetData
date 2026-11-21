# -*- coding: utf-8 -*-
"""绘图 golden 测试：渲染结果与基线 PNG 的像素差异不超过阈值。"""

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PyQt5.QtGui import QImage  # noqa: E402

from golden_cases import CASES, app, render_case  # noqa: E402

GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'golden')
MAX_DIFF = 0.01  # 1% 像素差异，容忍字体/抗锯齿的微小变化


class GoldenDrawingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app()
        os.makedirs(GOLDEN, exist_ok=True)

    def test_golden(self):
        for name in CASES:
            with self.subTest(case=name):
                pm = render_case(name)
                self.assertIsNotNone(pm)
                actual = pm.toImage().convertToFormat(QImage.Format_RGB32)
                path = os.path.join(GOLDEN, name + '.png')
                if not os.path.isfile(path):
                    if os.environ.get('UPDATE_GOLDEN') == '1':
                        actual.save(path, 'PNG')
                        continue
                    self.fail('缺少 golden 基线：%s；先运行 '
                              'python tools/update_golden.py' % path)
                base = QImage(path).convertToFormat(QImage.Format_RGB32)
                self.assertEqual(actual.size(), base.size(), name)
                a = actual.bits().asstring(actual.byteCount())
                b = base.bits().asstring(base.byteCount())
                total = actual.width() * actual.height()
                diff = sum(1 for i in range(0, len(a), 4)
                           if a[i:i + 4] != b[i:i + 4])
                ratio = diff / max(1, total)
                self.assertLessEqual(
                    ratio, MAX_DIFF,
                    '%s 像素差异 %.3f%% > %.1f%%' % (name, ratio * 100,
                                                     MAX_DIFF * 100))


if __name__ == '__main__':
    unittest.main()
