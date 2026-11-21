# -*- coding: utf-8 -*-
"""绘图 golden 用例的统一定义，测试与基线更新脚本共用。"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from flange_drawing import render_gb_flange  # noqa: E402
from parts_drawing import render_fitting, render_gasket, render_pipe  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402
import main  # noqa: E402


def _row(csvf, **where):
    _head, rows = main.load_csv(os.path.join(ROOT, 'Data', csvf))
    for row in rows:
        if all(str(row.get(k)) == str(v) for k, v in where.items()):
            return row
    return rows[0]


def render_case(name):
    if name == 'flange_rf':
        return render_gb_flange(_row('HGT20592_带颈对焊.csv', DN='50', PN='16'),
                                frame=False, kind='WN', compact=True,
                                face='RF')
    if name == 'flange_mfm':
        return render_gb_flange(_row('HGT20592_带颈对焊.csv', DN='50', PN='16'),
                                frame=False, kind='WN', compact=True,
                                face='MFM')
    if name == 'elbow_90':
        return render_fitting(_row('GB12459_弯头.csv', DN='50'),
                              'fittings_elbow.bmp', angle=90)
    if name == 'gasket_flat':
        return render_gasket(_row('HGT20606_RF.csv', DN='50'),
                             'gasket_flat.bmp')
    if name == 'pipe':
        return render_pipe(_row('GB17395_普通钢管.csv', DN='50'), 'pipe.bmp')
    raise KeyError(name)


CASES = ('flange_rf', 'flange_mfm', 'elbow_90', 'gasket_flat', 'pipe')


def app():
    return QApplication.instance() or QApplication([])
