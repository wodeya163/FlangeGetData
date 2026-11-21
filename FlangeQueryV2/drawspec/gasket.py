# -*- coding: utf-8 -*-
"""垫片的 DrawingSpec 适配器。"""

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QColor, QPainterPath, QPen

from drawspec.layout import DimensionLayout
from drawspec.spec import DrawingSpec

INK = QColor('#111111')
FILL = QColor('#eef2f7')
DIM = QColor('#5f6b76')
CENTER = QColor('#0b4f8a')


def _f(row, key, default=0.0):
    try:
        return float(str(row.get(key, '')).strip())
    except (TypeError, ValueError):
        return default


def build_gasket_spec(row, subtype='flat', width=800, height=500):
    a = _f(row, 'D1')
    b = _f(row, 'D2')
    if a <= 0 or b <= 0:
        return None
    outer, inner = max(a, b), min(a, b)
    t = _f(row, 'T', 3.0)
    scale = min((width - 220) / outer, (height - 200) / max(t, 1))
    cx, cy = width / 2, height / 2
    half = max(8.0, t * scale / 2)
    spec = DrawingSpec(title='垫片 %s  DN%s  D1=%s  D2=%s  T=%s' % (
        (row.get('型式') or subtype), row.get('DN', ''),
        row.get('D1', ''), row.get('D2', ''), row.get('T', '')),
        width=width, height=height, source=row.get('标准', ''))

    def X(v):
        return cx + v * scale

    for sign in (-1, 1):
        p = QPainterPath()
        x1, x2 = X(sign * outer / 2), X(sign * inner / 2)
        p.addRect(QRectF(min(x1, x2), cy - half, abs(x2 - x1), 2 * half))
        spec.path(p, QPen(INK, 2.2), FILL)
    # 中心孔上下平行线
    for yy in (cy - half, cy + half):
        p = QPainterPath()
        p.moveTo(X(-inner / 2), yy)
        p.lineTo(X(inner / 2), yy)
        spec.path(p, QPen(INK, 2.4))
    # 中心线
    p = QPainterPath()
    p.moveTo(cx, cy - half - 30)
    p.lineTo(cx, cy + half + 30)
    pen = QPen(CENTER, 1.5, Qt.DashDotLine)
    pen.setDashPattern([10, 3, 2, 3])
    spec.path(p, pen)

    layout = DimensionLayout(width, height, 14)
    y, pos = layout.place_horizontal(X(-a / 2), X(a / 2), 'D1=%s' %
                                     row.get('D1', ''), cy - half - 46)
    spec.dimension(QPointF(X(-a / 2), y), QPointF(X(a / 2), y),
                   'D1=%s' % row.get('D1', ''),
                   ext1=(X(-a / 2), cy - half), ext2=(X(a / 2), cy - half),
                   text_pos=pos)
    y2, pos2 = layout.place_horizontal(X(-b / 2), X(b / 2), 'D2=%s' %
                                       row.get('D2', ''), cy + half + 46)
    spec.dimension(QPointF(X(-b / 2), y2), QPointF(X(b / 2), y2),
                   'D2=%s' % row.get('D2', ''),
                   ext1=(X(-b / 2), cy + half), ext2=(X(b / 2), cy + half),
                   text_pos=pos2)
    x, tpos = layout.place_vertical(cy - half, cy + half,
                                    'T=%s' % row.get('T', ''), X(outer / 2) + 34)
    spec.dimension(QPointF(x, cy - half), QPointF(x, cy + half),
                   'T=%s' % row.get('T', ''),
                   ext1=(X(outer / 2), cy - half),
                   ext2=(X(outer / 2), cy + half), text_pos=tpos)
    spec.text(24, 62, '数据源：%s' % row.get('标准', ''), 12,
              QColor('#555555'))
    spec.text(24, 84, '参数化矢量图 · 尺寸单位 mm', 12, QColor('#555555'))
    return spec
