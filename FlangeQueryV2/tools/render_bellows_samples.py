# -*- coding: utf-8 -*-
"""生成波纹伸缩节矢量验证样张。"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.pop('QT_QPA_PLATFORM', None)

from PyQt5.QtWidgets import QApplication  # noqa: E402

import main  # noqa: E402
from bellows_drawing import render_bellows  # noqa: E402

OUT = os.path.join(ROOT, 'docs', 'assets')


def main_entry():
    app = QApplication([])
    _head, rows = main.load_csv(os.path.join(ROOT, 'Data', 'U_bellows.csv'))
    by_dn = {}
    for row in rows:
        by_dn.setdefault(row['DN'], row)
    for dn in ('50', '200', '1000', '2800'):
        pixmap = render_bellows(by_dn[dn], 1200, 900, frame=True)
        path = os.path.join(OUT, 'bellows_vector_dn%s.png' % dn)
        pixmap.save(path)
        print(path)
    app.quit()


if __name__ == '__main__':
    main_entry()
