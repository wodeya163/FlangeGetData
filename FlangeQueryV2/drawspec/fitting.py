# -*- coding: utf-8 -*-
"""弯头的 DrawingSpec 适配器（正投影 + 圆弧中心线）。"""

import math

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QColor, QPainterPath, QPen

from drawspec.spec import DrawingSpec
from drawspec.wall import wall_for

INK = QColor('#111111')
DIM = QColor('#5f6b76')
CENTER = QColor('#0b4f8a')
FILL = QColor('#eef2f7')


def _f(row, key, default=0.0):
    try:
        return float(str(row.get(key, '')).strip())
    except (TypeError, ValueError):
        return default


def build_elbow_spec(row, angle=90, width=800, height=500, standard='',
                     wall_series='Sch40'):
    od = _f(row, 'D_o_A') or _f(row, 'D_o')
    if od <= 0:
        return None
    angle = int(angle)
    if angle == 45:
        h_val = _f(row, 'H_45', od * 1.1)
    elif angle == 180:
        h_val = _f(row, 'A_180LR') or _f(row, 'P_180LR') or od * 2
    else:
        h_val = _f(row, 'F_90LR') or _f(row, 'F_90SR') or od * 1.5
    r_mm = od * 1.5
    scale = min(300 / max(od, h_val, r_mm), 4.0)
    R = max(40.0, r_mm * scale)
    wall_mm = wall_for(row, wall_series)
    wall = max(2.0, wall_mm * scale) if wall_mm > 0 else max(4.0, od * 0.08 * scale)
    ro, ri = R + od / 2 * scale, max(16.0, R - (od / 2 - wall_mm) * scale)
    span = math.radians(angle)
    steps = max(12, int(angle / 3))
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
    dx, dy = width / 2 - b.center().x(), height / 2 - b.center().y()

    def T(p):
        return QPointF(p.x() + dx, p.y() + dy)

    spec = DrawingSpec(
        title='%s°弯头  DN%s  D=%s  H=%g  R=%g' % (
            angle, row.get('DN', ''), row.get('D_o_A', ''), h_val, r_mm),
        width=width, height=height, source=standard)
    outer = QPainterPath()
    outer.moveTo(T(po[0]))
    for q in po[1:]:
        outer.lineTo(T(q))
    spec.path(outer, QPen(INK, 2.2))
    inner = QPainterPath()
    inner.moveTo(T(pi[0]))
    for q in pi[1:]:
        inner.lineTo(T(q))
    spec.path(inner, QPen(INK, 1.3, Qt.DashLine))
    caps = QPainterPath()
    caps.moveTo(T(po[0]))
    caps.lineTo(T(pi[0]))
    caps.moveTo(T(po[-1]))
    caps.lineTo(T(pi[-1]))
    spec.path(caps, QPen(INK, 2.2))
    center = QPainterPath()
    center.moveTo(T(pc[0]))
    for q in pc[1:]:
        center.lineTo(T(q))
    cpen = QPen(CENTER, 1.6, Qt.DashDotLine)
    cpen.setDashPattern([12, 4, 3, 4])
    spec.path(center, cpen)

    mid = T(pc[len(pc) // 2])
    endp = QPointF((T(po[-1]).x() + T(pi[-1]).x()) / 2,
                   (T(po[-1]).y() + T(pi[-1]).y()) / 2)
    spec.dimension(T(QPointF(0, 0)), mid, 'R=%g' % r_mm,
                   text_pos=QPointF(mid.x() - 42, mid.y() - 20))
    spec.dimension(T(QPointF(0, 0)), endp, 'H=%g' % h_val,
                   text_pos=QPointF(endp.x() + 10, endp.y() + 12))
    spec.dimension(T(po[-1]), T(pi[-1]), 'D=%s' % row.get('D_o_A', ''),
                   text_pos=QPointF(T(po[-1]).x() + 12,
                                    T(po[-1]).y() - 12))
    spec.text(24, 62, '数据源：%s' % (standard or '内置数据'), 12,
              QColor('#555555'))
    spec.text(24, 84, '参数化矢量图 · 尺寸单位 mm', 12, QColor('#555555'))
    return spec


def _fit_path(spec, path, width, height):
    box = path.boundingRect()
    dx = width / 2 - box.center().x()
    dy = height / 2 - box.center().y()
    path.translate(dx, dy)
    spec.path(path, QPen(INK, 2.2))
    return path.boundingRect(), dx, dy


def build_tee_spec(row, width=800, height=500, standard='',
                   wall_series='Sch40'):
    od = _f(row, 'D_o_A') or _f(row, 'D_o')
    if od <= 0:
        return None
    c = _f(row, 'C', od * 1.2)
    scale = min(280 / od, 2.0)
    w = max(80.0, c * scale)
    half = od / 2 * scale
    wall_mm = wall_for(row, wall_series)
    wall = max(2.0, wall_mm * scale) if wall_mm > 0 else max(4.0, half * 0.16)
    outer = QPainterPath()
    outer.addRect(QRectF(-w, -half, 2 * w, 2 * half))
    branch = QPainterPath()
    branch.addRect(QRectF(-half, -w, 2 * half, w))
    outer = outer.united(branch)
    inner = QPainterPath()
    iw = max(4.0, half - wall)
    inner.addRect(QRectF(-w + wall, -iw, 2 * (w - wall), 2 * iw))
    ib = QPainterPath()
    ib.addRect(QRectF(-iw, -w + wall, 2 * iw, w - wall))
    inner = inner.united(ib)
    spec = DrawingSpec(title='等径三通 DN%s  D=%s  C=%s' % (
        row.get('DN', ''), row.get('D_o_A', ''), row.get('C', '')),
        width=width, height=height, source=standard)
    rect, dx, dy = _fit_path(spec, outer, width, height)
    inner.translate(dx, dy)
    spec.path(inner, QPen(INK, 1.2, Qt.DashLine))
    # 支管与主管相贯线：外壁实线、内壁虚线
    cx, cy = width / 2, height / 2
    sag = max(4.0, half * 0.28)
    for y0, dashed in ((cy - half, False), (cy - half + wall, True)):
        p = QPainterPath()
        p.moveTo(cx - half, y0)
        p.cubicTo(cx - half * 0.45, y0 + sag,
                  cx + half * 0.45, y0 + sag,
                  cx + half, y0)
        spec.path(p, QPen(INK, 1.1 if dashed else 1.5,
                          Qt.DashLine if dashed else Qt.SolidLine))
    center = QPainterPath()
    center.moveTo(width / 2 - w, height / 2)
    center.lineTo(width / 2 + w, height / 2)
    center.moveTo(width / 2, height / 2 - w)
    center.lineTo(width / 2, height / 2)
    cp = QPen(CENTER, 1.5, Qt.DashDotLine)
    cp.setDashPattern([12, 4, 3, 4])
    spec.path(center, cp)
    # 端部坡口
    bevel = max(2.0, wall * 0.8)
    bpath = QPainterPath()
    cx, cy = width / 2, height / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = cx + sx * w, cy + sy * half
            bpath.moveTo(x, y)
            bpath.lineTo(x - sx * bevel, y - sy * (half - wall))
    for sx in (-1, 1):
        x, y = cx + sx * half, cy - w
        bpath.moveTo(x, y)
        bpath.lineTo(x - sx * (half - wall), y + bevel)
    spec.path(bpath, QPen(INK, 1.4))
    spec.dimension(QPointF(width / 2 - w, height / 2 + half + 28),
                   QPointF(width / 2 + w, height / 2 + half + 28),
                   'C=%s' % row.get('C', ''),
                   text_pos=QPointF(width / 2, height / 2 + half + 8))
    spec.dimension(QPointF(width / 2 + w + 30, height / 2 - half),
                   QPointF(width / 2 + w + 30, height / 2 + half),
                   'D=%s' % row.get('D_o_A', ''),
                   text_pos=QPointF(width / 2 + w + 52, height / 2))
    spec.text(24, 62, '数据源：%s' % (standard or '内置数据'), 12,
              QColor('#555555'))
    spec.text(24, 84, '参数化矢量图 · 尺寸单位 mm', 12, QColor('#555555'))
    return spec


def build_reducer_spec(row, width=800, height=500, standard='',
                       wall_series='Sch40'):
    od = _f(row, 'D_o_A') or _f(row, 'D_o')
    if od <= 0:
        return None
    scale = min(280 / od, 2.5)
    r1 = od / 2 * scale
    r2 = max(6.0, (_f(row, 'D_o_B', od * 0.7) / 2) * scale)
    h = max(100.0, min(240.0, _f(row, 'H', 100) * 0.9))
    wall_mm = wall_for(row, wall_series)
    wall = max(2.0, wall_mm * scale) if wall_mm > 0 else max(4.0, r1 * 0.08)
    outer = QPainterPath()
    outer.moveTo(-r1, -h / 2)
    outer.lineTo(r1, -h / 2)
    outer.lineTo(r2, h / 2)
    outer.lineTo(-r2, h / 2)
    outer.closeSubpath()
    inner = QPainterPath()
    inner.moveTo(-max(2, r1 - wall), -h / 2)
    inner.lineTo(max(2, r1 - wall), -h / 2)
    inner.lineTo(max(2, r2 - wall), h / 2)
    inner.lineTo(-max(2, r2 - wall), h / 2)
    inner.closeSubpath()
    spec = DrawingSpec(title='异径管 DN%s  D1=%s  D2=%s  H=%s' % (
        row.get('DN', ''), row.get('D_o_A', ''), row.get('D_o_B', ''),
        row.get('H', '')), width=width, height=height, source=standard)
    rect, dx, dy = _fit_path(spec, outer, width, height)
    inner.translate(dx, dy)
    spec.path(inner, QPen(INK, 1.2, Qt.DashLine))
    center = QPainterPath()
    center.moveTo(width / 2, height / 2 - h / 2 - 20)
    center.lineTo(width / 2, height / 2 + h / 2 + 20)
    cp = QPen(CENTER, 1.5, Qt.DashDotLine)
    cp.setDashPattern([12, 4, 3, 4])
    spec.path(center, cp)
    cx, cy = width / 2, height / 2
    bevel = max(2.0, wall * 0.8)
    bpath = QPainterPath()
    for sx in (-1, 1):
        bpath.moveTo(cx + sx * r1, cy - h / 2)
        bpath.lineTo(cx + sx * r1, cy - h / 2 + bevel)
        bpath.moveTo(cx + sx * r2, cy + h / 2)
        bpath.lineTo(cx + sx * r2, cy + h / 2 - bevel)
    spec.path(bpath, QPen(INK, 1.4))
    spec.dimension(QPointF(cx - r1, cy - h / 2 - 30),
                   QPointF(cx + r1, cy - h / 2 - 30),
                   'D1=%s' % row.get('D_o_A', ''),
                   text_pos=QPointF(cx, cy - h / 2 - 48))
    spec.dimension(QPointF(cx - r2, cy + h / 2 + 30),
                   QPointF(cx + r2, cy + h / 2 + 30),
                   'D2=%s' % row.get('D_o_B', ''),
                   text_pos=QPointF(cx, cy + h / 2 + 48))
    spec.dimension(QPointF(width / 2 + r1 + 26, height / 2 - h / 2),
                   QPointF(width / 2 + r1 + 26, height / 2 + h / 2),
                   'H=%s' % row.get('H', ''),
                   text_pos=QPointF(width / 2 + r1 + 48, height / 2))
    spec.text(24, 62, '数据源：%s' % (standard or '内置数据'), 12,
              QColor('#555555'))
    spec.text(24, 84, '参数化矢量图 · 尺寸单位 mm', 12, QColor('#555555'))
    return spec


def build_cap_spec(row, width=800, height=500, standard='',
                   wall_series='Sch40'):
    od = _f(row, 'D_o_A') or _f(row, 'D_o')
    if od <= 0:
        return None
    e_raw = _f(row, 'E', od * 1.2)
    e1_raw = _f(row, 'E1', e_raw)
    total = max(e_raw, e1_raw)
    straight_mm = min(e_raw, e1_raw)
    if total - straight_mm < max(1.0, od * 0.03):
        straight_mm = total * 0.65
    scale = min(300 / max(total, od), 3.0)
    r = od / 2 * scale
    length = total * scale
    straight = straight_mm * scale
    wall_mm = wall_for(row, wall_series)
    wall = max(2.0, wall_mm * scale) if wall_mm > 0 else max(4.0, r * 0.08)
    left, right = width / 2 - length / 2, width / 2 + length / 2
    base = left + straight
    cy = height / 2
    head = max(1.0, right - base)

    def dome_points(radius, x0, y0, steps=28):
        pts = [(x0, y0 - radius)]
        for i in range(1, steps + 1):
            t = math.pi / 2 * i / steps
            pts.append((x0 + head * math.sin(t),
                        y0 - radius * math.cos(t)))
        return pts

    top = [(left, cy - r), (base, cy - r)] + dome_points(r, base, cy)[1:]
    bottom = [(x, 2 * cy - y) for x, y in top]
    outer = QPainterPath()
    outer.moveTo(*top[0])
    for q in top[1:]:
        outer.lineTo(*q)
    for q in reversed(bottom[1:]):
        outer.lineTo(*q)
    outer.lineTo(*bottom[0])
    outer.closeSubpath()
    spec = DrawingSpec(title='椭圆管帽 DN%s  D=%s  E=%g  E1=%g' % (
        row.get('DN', ''), row.get('D_o_A', ''), straight_mm, total), width=width, height=height, source=standard)
    spec.path(outer, QPen(INK, 2.2), FILL)
    inner_top = [(left, cy - r + wall), (base, cy - r + wall)] +         dome_points(r - wall, base, cy)[1:]
    inner_bottom = [(x, 2 * cy - y) for x, y in inner_top]
    inner = QPainterPath()
    inner.moveTo(*inner_top[0])
    for q in inner_top[1:]:
        inner.lineTo(*q)
    for q in reversed(inner_bottom[1:]):
        inner.lineTo(*q)
    inner.lineTo(*inner_bottom[0])
    inner.closeSubpath()
    spec.path(inner, QPen(INK, 1.2, Qt.DashLine))
    endface = QPainterPath()
    endface.moveTo(left, cy - r)
    endface.lineTo(left, cy + r)
    endface.moveTo(base, cy - r)
    endface.lineTo(base, cy + r)
    spec.path(endface, QPen(INK, 1.4))
    center = QPainterPath()
    center.moveTo(left - 18, cy)
    center.lineTo(right + 18, cy)
    cp = QPen(CENTER, 1.5, Qt.DashDotLine)
    cp.setDashPattern([12, 4, 3, 4])
    spec.path(center, cp)
    spec.dimension(QPointF(left, cy - r - 30), QPointF(right, cy - r - 30),
                   'E1=%g' % total,
                   ext1=(left, cy - r), ext2=(right, cy - r),
                   text_pos=QPointF(width / 2, cy - r - 48))
    spec.dimension(QPointF(left - 26, cy - r), QPointF(left - 26, cy + r),
                   'D=%s' % row.get('D_o_A', ''),
                   text_pos=QPointF(left - 50, cy))
    spec.text(24, 62, '数据源：%s' % (standard or '内置数据'), 12,
              QColor('#555555'))
    spec.text(24, 84, 'E=%g  E1=%g  壁厚示意 %.2f mm' % (
        straight_mm, total, wall / scale), 12, QColor('#555555'))
    return spec
