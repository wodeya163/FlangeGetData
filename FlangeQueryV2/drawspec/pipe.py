# -*- coding: utf-8 -*-
"""钢管的 DrawingSpec 适配器。"""

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QColor, QPainterPath, QPen

from drawspec.layout import DimensionLayout
from drawspec.spec import DrawingSpec

INK = QColor('#111111')
FILL = QColor('#eef2f7')
CENTER = QColor('#0b4f8a')
DIM = QColor('#5f6b76')


def _f(row, key, default=0.0):
    try:
        return float(str(row.get(key, '')).strip())
    except (TypeError, ValueError):
        return default


def _wall(row):
    for key in ('壁厚S(mm)', 'S', 'S_min', 'Sch40', 'STD', 'Sch80',
                'Sch10s', 'Sch5s', 'PN25', 'PN40'):
        v = _f(row, key)
        if v > 0:
            return v
    return 2.0


def build_pipe_spec(row, width=800, height=500):
    od = _f(row, 'D_o') or _f(row, 'D_o_A')
    if od <= 0:
        return None
    wall = _wall(row)
    idia = max(1.0, od - 2 * wall)
    cx, cy = width / 2, height / 2
    scale = min((width - 260) / od, (height - 220) / od)
    ro, ri = od / 2 * scale, idia / 2 * scale
    spec = DrawingSpec(title='钢管 DN%s / %s  D_o=%s  S=%g' % (
        row.get('DN', ''), row.get('DN2', ''), row.get('D_o', ''), wall),
        width=width, height=height, source='GB/T 17395 / ASME B36.10M')
    outer = QPainterPath()
    outer.addEllipse(QPointF(cx, cy), ro, ro)
    spec.path(outer, QPen(INK, 2.2), FILL)
    inner = QPainterPath()
    inner.addEllipse(QPointF(cx, cy), ri, ri)
    spec.path(inner, QPen(INK, 2.2), QColor('#ffffff'))
    center = QPainterPath()
    center.moveTo(cx - ro - 20, cy)
    center.lineTo(cx + ro + 20, cy)
    center.moveTo(cx, cy - ro - 20)
    center.lineTo(cx, cy + ro + 20)
    pen = QPen(CENTER, 1.5, Qt.DashDotLine)
    pen.setDashPattern([12, 4, 3, 4])
    spec.path(center, pen)

    layout = DimensionLayout(width, height, 14)
    y, pos = layout.place_horizontal(cx - ro, cx + ro,
                                     'D=%s' % row.get('D_o', ''),
                                     cy - ro - 46)
    spec.dimension(QPointF(cx - ro, y), QPointF(cx + ro, y),
                   'D=%s' % row.get('D_o', ''),
                   ext1=(cx - ro, cy - ro), ext2=(cx + ro, cy - ro),
                   text_pos=pos)
    x, tpos = layout.place_vertical(cy - ro, cy - ri, 'S=%g' % wall,
                                    cx + ro * 0.62)
    spec.dimension(QPointF(x, cy - ro), QPointF(x, cy - ri),
                   'S=%g' % wall, ext1=(x, cy - ro), ext2=(x, cy - ri),
                   text_pos=tpos)
    spec.text(24, 62, '数据源：%s' % (spec.source or '内置数据'), 12,
              QColor('#555555'))
    spec.text(24, 84, '参数化矢量图 · 尺寸单位 mm', 12, QColor('#555555'))
    return spec
