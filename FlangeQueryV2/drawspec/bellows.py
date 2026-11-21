# -*- coding: utf-8 -*-
"""U 形波纹管 DrawingSpec：按 70B125 的圆弧-公切线波形成型。"""

import math

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QPainterPath, QPen

from bellows_drawing import pipeline, _wave_points
from drawspec.layout import DimensionLayout
from drawspec.spec import DrawingSpec

INK = QColor('#111111')
FILL = QColor('#eef2f7')
CENTER = QColor('#0b4f8a')


def _f(value, default=0.0):
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def build_bellows_spec(row, width=1200, height=760):
    _spec, pipe_od, wall = pipeline(row)
    d_o = _f(row.get('D_o'), pipe_od)
    h = _f(row.get('h'), 8)
    q = _f(row.get('q'), 8)
    r = _f(row.get('r'), 1.5)
    lt = _f(row.get('Lt'), 15)
    n = max(1, int(_f(row.get('N'), 4)))
    if d_o <= 0 or q <= 0:
        return None
    root_r = d_o / 2.0
    crest_r = root_r + h
    pipe_r = pipe_od / 2.0
    total_l = 2 * lt + n * q
    max_r = max(pipe_r, crest_r)
    scale = min((width - 300) / max(total_l, 1),
                (height - 300) / max(2 * max_r, 1))
    x0 = (width - total_l * scale) / 2
    cy = height / 2 + 10

    def X(mm):
        return x0 + mm * scale

    def Y(radius):
        return cy - radius * scale

    wave = _wave_points(q, h, r)
    bevel = max(2.0, wall * 1.87)
    end_r = max(wall, pipe_r - wall * 0.5)
    top = [(0.0, end_r), (bevel, pipe_r), (lt, pipe_r)]
    if abs(pipe_r - root_r) > 1e-6:
        top.append((lt, root_r))
    for i in range(n):
        for wx, wy in wave:
            top.append((lt + i * q + wx, root_r + wy))
    if abs(pipe_r - root_r) > 1e-6:
        top.append((lt + n * q, pipe_r))
    top.append((total_l - bevel, pipe_r))
    top.append((total_l, end_r))

    spec = DrawingSpec(
        title='U形波纹管  DN%s  L=%.1f  D_o=%s  h=%s  N=%d' % (
            row.get('DN', ''), total_l, row.get('D_o', ''),
            row.get('h', ''), n),
        width=width, height=height, source='70B125-2002 表A.1')
    outer = QPainterPath()
    outer.moveTo(X(0), Y(top[0][1]))
    for x, y in top:
        outer.lineTo(X(x), Y(y))
    outer.lineTo(X(total_l), Y(-top[-1][1]))
    for x, y in reversed(top):
        outer.lineTo(X(x), Y(-y))
    outer.lineTo(X(0), Y(-top[0][1]))
    outer.closeSubpath()
    spec.path(outer, QPen(INK, 2.2), FILL)

    wb = max(1.0, wall * 0.45)
    inner = QPainterPath()
    inner.moveTo(X(0), Y(top[0][1] - wb))
    for x, y in top:
        inner.lineTo(X(x), Y(y - wb))
    inner.lineTo(X(total_l), Y(-(top[-1][1] - wb)))
    for x, y in reversed(top):
        inner.lineTo(X(x), Y(-(y - wb)))
    inner.lineTo(X(0), Y(-(top[0][1] - wb)))
    inner.closeSubpath()
    spec.path(inner, QPen(INK, 1.2, Qt.DashLine), QColor('#ffffff'))

    center = QPainterPath()
    center.moveTo(20, cy)
    center.lineTo(width - 20, cy)
    cpen = QPen(CENTER, 1.5, Qt.DashDotLine)
    cpen.setDashPattern([12, 4, 3, 4])
    spec.path(center, cpen)

    layout = DimensionLayout(width, height, 14)
    y, pos = layout.place_horizontal(X(0), X(total_l), 'L=%.1f' % total_l,
                                     Y(crest_r) - 44)
    spec.dimension(QPointF(X(0), y), QPointF(X(total_l), y),
                   'L=%.1f' % total_l,
                   ext1=(X(0), Y(crest_r)), ext2=(X(total_l), Y(crest_r)),
                   text_pos=pos)
    x, pos2 = layout.place_vertical(Y(crest_r), Y(-crest_r),
                                    'D=%s' % row.get('D_o', ''),
                                    X(total_l) + 34)
    spec.dimension(QPointF(x, Y(crest_r)), QPointF(x, Y(-crest_r)),
                   'D=%s' % row.get('D_o', ''),
                   ext1=(X(total_l), Y(crest_r)),
                   ext2=(X(total_l), Y(-crest_r)), text_pos=pos2)
    spec.text(24, 62, '数据源：70B125-2002 表A.1', 12, QColor('#555555'))
    spec.text(24, 84, '波高 h=%s  波距 q=%s  圆弧 r=%s  N=%d  单位 mm' % (
        row.get('h', ''), row.get('q', ''), row.get('r', ''), n),
        12, QColor('#555555'))
    return spec
