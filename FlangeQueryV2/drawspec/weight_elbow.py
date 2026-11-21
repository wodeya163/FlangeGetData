# -*- coding: utf-8 -*-
"""弯头重量页的矢量示意图。"""

import math

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QPainterPath, QPen

from drawspec.spec import DrawingSpec

INK = QColor('#111111')
DIM = QColor('#5f6b76')
CENTER = QColor('#0b4f8a')


def build_elbow_weight_spec(od, wall, radius, angle, density,
                            width=760, height=270, kind='标准弯头',
                            tangent1=0.0, tangent2=0.0):
    if od <= 0 or wall <= 0 or radius <= 0 or angle <= 0:
        return None
    angle = min(float(angle), 360.0)
    span = math.radians(angle)
    scale = min(1.6, 300.0 / max(2 * radius + od, 1))
    scale = max(0.05, scale)
    R = radius * scale
    ro = R + od / 2 * scale
    ri = max(4.0, R - (od / 2 - wall) * scale)
    steps = max(16, int(angle / 3))
    po, pi, pc = [], [], []
    for k in range(steps + 1):
        th = math.pi + span * k / steps
        po.append(QPointF(ro * math.cos(th), ro * math.sin(th)))
        pi.append(QPointF(ri * math.cos(th), ri * math.sin(th)))
        pc.append(QPointF(R * math.cos(th), R * math.sin(th)))
    box = QPainterPath()
    box.moveTo(po[0])
    for q in po[1:]:
        box.lineTo(q)
    for q in pi:
        box.lineTo(q)
    b = box.boundingRect()
    dx = width / 2 - b.center().x()
    dy = height / 2 - b.center().y()

    def T(p):
        return QPointF(p.x() + dx, p.y() + dy)

    spec = DrawingSpec(
        title='%s  D=%g mm  S=%g mm  R=%g mm  θ=%g°' % (kind,
            od, wall, radius, angle),
        width=width, height=height, source='重量计算')
    outer = QPainterPath()
    outer.moveTo(T(po[0]))
    for q in po[1:]:
        outer.lineTo(T(q))
    spec.path(outer, QPen(INK, 2.2))
    inner = QPainterPath()
    inner.moveTo(T(pi[0]))
    for q in pi[1:]:
        inner.lineTo(T(q))
    spec.path(inner, QPen(INK, 1.2, Qt.DashLine))
    caps = QPainterPath()
    caps.moveTo(T(po[0]))
    caps.lineTo(T(pi[0]))
    caps.moveTo(T(po[-1]))
    caps.lineTo(T(pi[-1]))
    spec.path(caps, QPen(INK, 2.0))
    center = QPainterPath()
    center.moveTo(T(pc[0]))
    for q in pc[1:]:
        center.lineTo(T(q))
    cp = QPen(CENTER, 1.4, Qt.DashDotLine)
    cp.setDashPattern([10, 3, 2, 3])
    spec.path(center, cp)

    mid = T(pc[len(pc) // 2])
    spec.dimension(T(QPointF(0, 0)), mid, 'R=%g' % radius,
                   text_pos=QPointF(mid.x() - 38, mid.y() - 18))
    spec.dimension(T(po[-1]), T(pi[-1]), 'D=%g' % od,
                   text_pos=QPointF(T(po[-1]).x() + 10,
                                    T(po[-1]).y() - 12))
    spec.text(24, 58, 'θ=%g°  ·  S=%g mm  ·  D=%g mm  ·  R=%g mm'
              % (angle, wall, od, radius), 12, QColor('#555555'))
    note = 'ρ=%g kg/m³  ·  按中心线弧长计算' % density
    if tangent1 or tangent2:
        note = ('ρ=%g kg/m³  ·  弧长 + 直段 L1=%g / L2=%g mm'
                % (density, tangent1, tangent2))
    spec.text(24, 78, note, 11, QColor('#888888'))
    return spec
