# -*- coding: utf-8 -*-
"""三通重量页的矢量示意图（标准 / 斜 / 弯三通）。"""

import math

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QColor, QPainterPath, QPen

from drawspec.spec import DrawingSpec

INK = QColor('#111111')
FILL = QColor('#eef2f7')
CENTER = QColor('#0b4f8a')
DIM = QColor('#5f6b76')


def _polyline_path(points, half_width):
    """把中心线折线扩展成等宽管状多边形。"""
    if len(points) < 2:
        return QPainterPath()
    left, right = [], []
    for i, p in enumerate(points):
        if i == 0:
            dx = points[1].x() - p.x()
            dy = points[1].y() - p.y()
        elif i == len(points) - 1:
            dx = p.x() - points[i - 1].x()
            dy = p.y() - points[i - 1].y()
        else:
            dx = points[i + 1].x() - points[i - 1].x()
            dy = points[i + 1].y() - points[i - 1].y()
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln * half_width, dx / ln * half_width
        left.append(QPointF(p.x() + nx, p.y() + ny))
        right.append(QPointF(p.x() - nx, p.y() - ny))
    path = QPainterPath()
    path.moveTo(left[0])
    for p in left[1:]:
        path.lineTo(p)
    for p in reversed(right):
        path.lineTo(p)
    path.closeSubpath()
    return path


def _centerline(points):
    path = QPainterPath()
    path.moveTo(points[0])
    for p in points[1:]:
        path.lineTo(p)
    return path


def build_tee_weight_spec(kind, od_main, od_branch, wall, main_length,
                          branch_length=100.0, angle=90.0,
                          bend_radius=0.0, density=7850.0,
                          width=760, height=270):
    """kind: 标准三通 / 斜三通 / 弯三通。"""
    if od_main <= 0 or od_branch <= 0 or wall <= 0:
        return None
    cx, cy = width * 0.46, height * 0.66
    main_half = max(16.0, min(42.0, od_main * 0.32))
    branch_half = max(14.0, min(36.0, od_branch * 0.32))
    wall_w = max(3.0, min(main_half * 0.35, wall / od_main * main_half))
    x0, x1 = 95.0, width - 95.0
    spec = DrawingSpec(
        title='%s  D主=%g mm  D支=%g mm  S=%g mm' % (
            kind, od_main, od_branch, wall),
        width=width, height=height, source='重量计算')

    main_outer = _polyline_path(
        [QPointF(x0, cy), QPointF(x1, cy)], main_half)
    main_inner = _polyline_path(
        [QPointF(x0, cy), QPointF(x1, cy)],
        max(2.0, main_half - wall_w))

    if kind == '斜三通':
        theta = math.radians(max(5.0, min(175.0, angle)))
        direction = QPointF(math.cos(theta), -math.sin(theta))
        length = max(70.0, min(155.0, branch_length * 0.55))
        end = QPointF(cx + direction.x() * length,
                      cy + direction.y() * length)
        branch_points = [QPointF(cx, cy), end]
    elif kind == '弯三通':
        straight = 62.0
        r = max(24.0, min(52.0, bend_radius * 0.18 if bend_radius else 38.0))
        tail = 48.0
        branch_points = [QPointF(cx, cy), QPointF(cx, cy - straight)]
        for i in range(1, 13):
            a = math.pi + (math.pi / 2) * i / 12.0
            branch_points.append(QPointF(cx + r + r * math.cos(a),
                                         cy - straight + r * math.sin(a)))
        branch_points.append(QPointF(cx + r + tail, cy - straight - r))
    else:
        length = max(80.0, min(145.0, branch_length * 0.55))
        branch_points = [QPointF(cx, cy), QPointF(cx, cy - length)]

    branch_outer = _polyline_path(branch_points, branch_half)
    branch_inner = _polyline_path(branch_points,
                                  max(2.0, branch_half - wall_w))

    # 支管在外、主管覆盖交接处，保持“三通”轮廓
    spec.path(branch_outer, QPen(INK, 2.0), FILL)
    spec.path(main_outer, QPen(INK, 2.2), FILL)
    spec.path(branch_inner, QPen(INK, 1.1, Qt.DashLine), QColor('#ffffff'))
    spec.path(main_inner, QPen(INK, 1.1, Qt.DashLine), QColor('#ffffff'))
    spec.path(_centerline(branch_points), QPen(CENTER, 1.3, Qt.DashDotLine))
    spec.path(_centerline([QPointF(x0 - 14, cy), QPointF(x1 + 14, cy)]),
              QPen(CENTER, 1.3, Qt.DashDotLine))

    # 尺寸
    spec.dimension(QPointF(x0, cy - main_half), QPointF(x0, cy + main_half),
                   'D主=%g' % od_main, text_pos=QPointF(x0 - 8, cy))
    spec.dimension(QPointF(x0, cy + main_half + 42),
                   QPointF(x1, cy + main_half + 42),
                   'L主=%g' % main_length,
                   ext1=(x0, cy + main_half), ext2=(x1, cy + main_half),
                   text_pos=QPointF((x0 + x1) / 2, cy + main_half + 26))
    if kind == '斜三通':
        spec.text(x0, height - 44,
                  'θ=%g°  ·  支管高度 %g mm' % (angle, branch_length),
                  12, QColor('#555555'))
        spec.text(x0, height - 24,
                  'ρ=%g kg/m³  ·  按支管斜长计算' % density,
                  10, QColor('#888888'))
    elif kind == '弯三通':
        spec.text(x0, height - 44,
                  'R=%g mm  ·  支管直段 %g mm' % (bend_radius,
                                                  branch_length),
                  12, QColor('#555555'))
        spec.text(x0, height - 24,
                  'ρ=%g kg/m³  ·  按直段 + 弯弧计算' % density,
                  10, QColor('#888888'))
    else:
        spec.text(x0, height - 44,
                  'L支=%g mm  ·  S=%g mm' % (branch_length, wall),
                  12, QColor('#555555'))
        spec.text(x0, height - 24,
                  'ρ=%g kg/m³  ·  按主管 + 支管中心线计算' % density,
                  10, QColor('#888888'))
    return spec
