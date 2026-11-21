# -*- coding: utf-8 -*-
"""生成/更新绘图 golden 基线。"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tests'))
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from golden_cases import CASES, app, render_case  # noqa: E402

OUT = os.path.join(ROOT, 'tests', 'golden')


def main():
    os.makedirs(OUT, exist_ok=True)
    _app = app()
    for name in CASES:
        pm = render_case(name)
        if pm is None:
            raise SystemExit('渲染失败：' + name)
        path = os.path.join(OUT, name + '.png')
        pm.save(path, 'PNG')
        print('已写入：', path)


if __name__ == '__main__':
    main()
