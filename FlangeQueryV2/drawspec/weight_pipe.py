# -*- coding: utf-8 -*-
"""直管重量页的矢量示意图。"""

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QPainterPath, QPen

from drawspec.spec import DrawingSpec

INK = QColor('#111111')
FILL = QColor('#eef2f7')
DIM = QColor('#5f6b76')
CENTER = QColor('#0b4f8a')


def build_pipe_weight_spec(od, wall, length_m, density, width=760,
                           height=270):
    """直管纵向示意：长度不按比例，D/S/L 标在图上。"""
    if od <= 0 or wall <= 0 or length_m <= 0:
        return None
    x0, x1 = 120, width - 120
    cy = 130
    r = max(28.0, min(58.0, od * 0.45))
    wt = max(4.0, min(r * 0.45, wall / od * 2 * r))
    spec = DrawingSpec(
        title='直管  D=%g mm  S=%g mm  L=%g m' % (od, wall, length_m),
        width=width, height=height, source='重量计算')
    outer = QPainterPath()
    outer.addRect(x0, cy - r, x1 - x0, 2 * r)
    spec.path(outer, QPen(INK, 2.2), FILL)
    inner = QPainterPath()
    inner.addRect(x0, cy - r + wt, x1 - x0, 2 * (r - wt))
    spec.path(inner, QPen(INK, 1.2, Qt.DashLine), QColor('#ffffff'))
    # 管端
    ends = QPainterPath()
    for x in (x0, x1):
        ends.moveTo(x, cy - r)
        ends.lineTo(x, cy + r)
    spec.path(ends, QPen(INK, 2.0))
    # 中心线
    center = QPainterPath()
    center.moveTo(x0 - 14, cy)
    center.lineTo(x1 + 14, cy)
    cp = QPen(CENTER, 1.4, Qt.DashDotLine)
    cp.setDashPattern([10, 3, 2, 3])
    spec.path(center, cp)

    # 外径 D
    spec.dimension(QPointF(x0 - 30, cy - r), QPointF(x0 - 30, cy + r),
                   'D=%g' % od,
                   text_pos=QPointF(x0 - 54, cy))
    # 长度 L（示意）
    spec.dimension(QPointF(x0, 64), QPointF(x1, 64), 'L=%g m' % length_m,
                   ext1=(x0, cy - r), ext2=(x1, cy - r),
                   text_pos=QPointF((x0 + x1) / 2, 46))
    # 壁厚 S：右端局部
    sx = x1 + 30
    spec.dimension(QPointF(sx, cy - r), QPointF(sx, cy - r + wt),
                   'S=%g' % wall,
                   text_pos=QPointF(sx + 28, cy - r + wt / 2))
    spec.text(x0, height - 28,
              'ρ=%g kg/m³  ·  D=%g mm  ·  S=%g mm  ·  L=%g m'
              % (density, od, wall, length_m),
              12, QColor('#555555'))
    spec.text(x0, height - 10, '长度方向为示意，不按比例', 10,
              QColor('#888888'))
    return spec
