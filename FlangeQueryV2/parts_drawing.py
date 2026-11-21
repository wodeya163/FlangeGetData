# -*- coding: utf-8 -*-
"""垫片/钢管/管件/密封面矢量示意图。"""

import math

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import (QColor, QPainter, QPainterPath, QPen, QPixmap,
                         QPolygonF)

import bellows_drawing as bd
from bellows_drawing import _arrow, _text
from drawspec.wall import wall_for

INK = QColor('#111111')
DIM = QColor('#5f6b76')
FILL = QColor('#eef2f7')
CENTER = QColor('#0b4f8a')


def _f(row, key, default=0.0):
    try:
        return float(str(row.get(key, '')).strip())
    except (TypeError, ValueError):
        return default


def _num(row, keys, default=0.0):
    for key in keys:
        value = _f(row, key)
        if value > 0:
            return value
    return default


def _dim_h(painter, y, x1, x2, text, size=18):
    painter.setPen(QPen(DIM, 1))
    _arrow(painter, QPointF(x1, y), QPointF(x2, y), 8)
    _text(painter, (x1 + x2) / 2 - 80, y - 20, text, size, DIM,
          Qt.AlignHCenter, 160, True)


def _dim_v(painter, x, y1, y2, text, size=18):
    painter.setPen(QPen(DIM, 1))
    _arrow(painter, QPointF(x, y1), QPointF(x, y2), 8)
    _text(painter, x - 70, (y1 + y2) / 2 - 10, text, size, DIM,
          Qt.AlignHCenter, 140, True)


def _centers(painter, points):
    pen = QPen(CENTER, 1.6, Qt.DashDotLine)
    pen.setDashPattern([12, 4, 3, 4])
    painter.setPen(pen)
    for p1, p2 in points:
        if not isinstance(p1, QPointF):
            p1 = QPointF(*p1)
        if not isinstance(p2, QPointF):
            p2 = QPointF(*p2)
        painter.drawLine(p1, p2)


def render_gasket(row, tpl='gasket_flat.bmp', width=800, height=500):
    d1 = _num(row, ('D1',))
    d2 = _num(row, ('D2',))
    d3 = _num(row, ('D3',))
    t = _num(row, ('T',), 3.0)
    if d1 <= 0 or d2 <= 0:
        return _render_ring_gasket(row, tpl, width, height)
    d1_row, d2_row = d1, d2
    outer = max(d1, d2)
    inner = min(d1, d2)
    d1, d2 = outer, inner
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.white)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    scale = min((width - 220) / d1, (height - 220) / max(t, 1))
    cx, cy = width / 2, height / 2
    half_t = max(8.0, t * scale / 2)

    def X(mm):
        return cx + mm * scale

    # 左右两个环形截面
    painter.setBrush(FILL)
    painter.setPen(QPen(INK, 2.2))
    for sign in (-1, 1):
        x1 = X(sign * outer / 2)
        x2 = X(sign * inner / 2)
        painter.drawRect(QRectF(min(x1, x2), cy - half_t,
                                abs(x2 - x1), 2 * half_t))

    # 型式细节
    if 'ptfe' in tpl:
        painter.setPen(QPen(QColor('#4a6fa5'), 1.2, Qt.DashLine))
        for sign in (-1, 1):
            for off in (3, 6):
                x1 = X(sign * (outer / 2 - off / scale))
                x2 = X(sign * (inner / 2 + off / scale))
                painter.drawLine(QPointF(min(x1, x2), cy - half_t + 2),
                                 QPointF(max(x1, x2), cy - half_t + 2))
                painter.drawLine(QPointF(min(x1, x2), cy + half_t - 2),
                                 QPointF(max(x1, x2), cy + half_t - 2))
    elif 'metaljacket' in tpl:
        painter.setPen(QPen(INK, 1.6))
        for sign in (-1, 1):
            x1, x2 = X(sign * outer / 2), X(sign * inner / 2)
            painter.drawRect(QRectF(min(x1, x2), cy - half_t + 4,
                                    abs(x2 - x1), 2 * half_t - 8))
        painter.setPen(QPen(QColor('#4a6fa5'), 1.2, Qt.DashLine))
        painter.drawLine(QPointF(X(-outer / 2 + 3 / scale), cy - half_t),
                         QPointF(X(-outer / 2 + 3 / scale), cy + half_t))

    # 内孔/中心线：中心孔上下两条平行实线
    painter.setPen(QPen(INK, 2.4))
    for sign in (-1, 1):
        painter.drawLine(QPointF(X(sign * inner / 2), cy - half_t),
                         QPointF(X(sign * inner / 2), cy + half_t))
    for yy in (cy - half_t, cy + half_t):
        painter.drawLine(QPointF(X(-inner / 2), yy),
                         QPointF(X(inner / 2), yy))
    _centers(painter, [((cx, cy - half_t - 30), (cx, cy + half_t + 30))])

    # 缠绕/齿形/金属环的示意线
    if 'spiral' in tpl:
        painter.setPen(QPen(QColor('#7b8794'), 1))
        for sign in (-1, 1):
            for k in (0.25, 0.5, 0.75):
                xx = X(sign * (d2 + (d1 - d2) * k) / 2)
                painter.drawLine(QPointF(xx, cy - half_t + 3),
                                 QPointF(xx, cy + half_t - 3))
    elif 'serrated' in tpl:
        painter.setPen(QPen(INK, 1))
        for sign in (-1, 1):
            x1, x2 = X(sign * d1 / 2), X(sign * d2 / 2)
            step = 6
            x = min(x1, x2)
            while x < max(x1, x2):
                painter.drawLine(QPointF(x, cy - half_t),
                                 QPointF(x + step / 2, cy - half_t - 3))
                painter.drawLine(QPointF(x + step / 2, cy - half_t - 3),
                                 QPointF(x + step, cy - half_t))
                x += step

    # 尺寸
    _dim_h(painter, cy - half_t - 55, X(-d1_row / 2), X(d1_row / 2),
           'D1=%s' % row.get('D1', ''))
    _dim_h(painter, cy + half_t + 55, X(-d2_row / 2), X(d2_row / 2),
           'D2=%s' % row.get('D2', ''))
    _dim_v(painter, X(d1 / 2) + 55, cy - half_t, cy + half_t,
           'T=%s' % row.get('T', ''))
    if d3 > 0 and d3 < d1:
        painter.setPen(QPen(DIM, 1, Qt.DashLine))
        painter.drawLine(QPointF(X(-d3 / 2), cy - half_t - 8),
                         QPointF(X(-d3 / 2), cy + half_t + 8))
        painter.drawLine(QPointF(X(d3 / 2), cy - half_t - 8),
                         QPointF(X(d3 / 2), cy + half_t + 8))
        _text(painter, cx - 100, cy + half_t + 24, 'D3=%s' % row.get('D3', ''),
              14, DIM, Qt.AlignHCenter, 200, True)

    # 密封面接触带、压缩方向与密封宽度 b
    b = _num(row, ('b',))
    if b > 0:
        _dim_h(painter, cy + half_t + 22, X(-outer / 2), X(-inner / 2),
               'b=%s' % row.get('b', ''), 14)
    painter.setPen(QPen(QColor('#2f6f9f'), 2.0))
    for sign in (-1, 1):
        x1, x2 = X(sign * outer / 2), X(sign * inner / 2)
        painter.drawLine(QPointF(min(x1, x2), cy - half_t),
                         QPointF(max(x1, x2), cy - half_t))
        painter.drawLine(QPointF(min(x1, x2), cy + half_t),
                         QPointF(max(x1, x2), cy + half_t))
    for sign in (-1, 1):
        xm = X(sign * (outer + inner) / 4)
        _arrow(painter, QPointF(xm, cy - half_t - 14),
               QPointF(xm, cy - half_t), 5)
        _arrow(painter, QPointF(xm, cy + half_t + 14),
               QPointF(xm, cy + half_t), 5)
    if row.get('P'):
        _text(painter, cx - 100, cy + half_t + 38, 'P=%s  压缩方向↑↓' % row.get('P'),
              12, DIM, Qt.AlignHCenter, 240, True)

    _text(painter, 24, 18, '垫片 %s' % ('/'.join(
        str(row.get(k, '')) for k in ('型式', '标准') if row.get(k))),
        18, INK, Qt.AlignLeft, 700)
    _text(painter, 24, 46, 'DN %s  PN/Class %s' % (
        row.get('DN', ''), row.get('PN', '') or row.get('Class', '')),
        14, QColor('#333'), Qt.AlignLeft, 700)
    painter.end()
    return pixmap



def _render_ring_gasket(row, tpl, width=800, height=500):
    p = _num(row, ('P',))
    a = _num(row, ('A',))
    h = _num(row, ('H',))
    if p <= 0 or a <= 0 or h <= 0:
        return None
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.white)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    scale = min((width - 220) / p, (height - 200) / h)
    cx, cy = width / 2, height / 2
    ow, iw = p / 2 * scale, max(1.0, p / 2 - a) * scale
    ht = h / 2 * scale
    cut = min(ow - iw, ht) * 0.35

    def octagon(half_w, half_h, c):
        return QPolygonF([
            QPointF(cx - half_w + c, cy - half_h),
            QPointF(cx + half_w - c, cy - half_h),
            QPointF(cx + half_w, cy - half_h + c),
            QPointF(cx + half_w, cy + half_h - c),
            QPointF(cx + half_w - c, cy + half_h),
            QPointF(cx - half_w + c, cy + half_h),
            QPointF(cx - half_w, cy + half_h - c),
            QPointF(cx - half_w, cy - half_h + c),
        ])

    outer = octagon(ow, ht, cut)
    inner = octagon(iw, max(1.0, ht - (ow - iw)), cut * 0.6)
    path = QPainterPath()
    path.addPolygon(outer)
    painter.setBrush(FILL)
    painter.setPen(QPen(INK, 2.2))
    painter.drawPath(path)
    painter.setBrush(Qt.white)
    painter.drawPolygon(inner)
    _centers(painter, [((cx, cy - ht - 25), (cx, cy + ht + 25))])
    _dim_h(painter, cy - ht - 50, cx - ow, cx + ow, 'P=%s' % row.get('P', ''))
    _dim_v(painter, cx + ow + 50, cy - ht, cy + ht, 'H=%s' % row.get('H', ''))
    _text(painter, cx - 100, cy + ht + 24, 'A=%s  r=%s' % (
        row.get('A', ''), row.get('r', '')), 14, DIM, Qt.AlignHCenter, 200)
    _text(painter, 24, 18, '金属环垫 %s' % row.get('型式', ''), 18, INK,
          Qt.AlignLeft, 700)
    _text(painter, 24, 46, 'DN %s  PN/Class %s' % (
        row.get('DN', ''), row.get('PN', '') or row.get('Class', '')),
        14, QColor('#333'), Qt.AlignLeft, 700)
    painter.end()
    return pixmap



def render_container(row, tpl='容器法兰.bmp', width=800, height=500):
    od = _num(row, ('D',))
    idia = _num(row, ('D4', 'D3'))
    h = _num(row, ('H', 'h'))
    if od <= 0 or idia <= 0 or h <= 0:
        return None
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.white)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    scale = min((width - 220) / od, (height - 220) / h)
    cx, cy = width / 2, height / 2
    ro, ri = od / 2 * scale, idia / 2 * scale
    ht = h / 2 * scale
    painter.setBrush(FILL)
    painter.setPen(QPen(INK, 2.2))
    for sign in (-1, 1):
        x1, x2 = cx + sign * ro, cx + sign * ri
        painter.drawRect(QRectF(min(x1, x2), cy - ht, abs(x1 - x2), 2 * ht))
    painter.setPen(QPen(INK, 2.4))
    for sign in (-1, 1):
        painter.drawLine(QPointF(cx + sign * ri, cy - ht),
                         QPointF(cx + sign * ri, cy + ht))

    # 螺栓孔与中心线（NB 数据：D1 螺栓圆、d/dta 孔径、n 数量）
    K = _num(row, ('K', 'D1'))
    hole_d = _num(row, ('d', 'dta'))
    n = int(_num(row, ('n',), 0))
    if K > 0 and hole_d > 0:
        hw = max(5.0, hole_d / 2 * scale)
        painter.setBrush(Qt.white)
        painter.setPen(QPen(INK, 1.4))
        for sign in (-1, 1):
            hx = cx + sign * K / 2 * scale
            painter.drawRect(QRectF(hx - hw, cy - ht, 2 * hw, 2 * ht))
        center_pen = QPen(CENTER, 1.5, Qt.DashDotLine)
        center_pen.setDashPattern([10, 3, 2, 3])
        painter.setPen(center_pen)
        for sign in (-1, 1):
            hx = cx + sign * K / 2 * scale
            painter.drawLine(QPointF(hx, cy - ht - 18),
                             QPointF(hx, cy + ht + 18))
            painter.drawLine(QPointF(hx - hw - 6, cy),
                             QPointF(hx + hw + 6, cy))
        _dim_h(painter, cy - ht - 78, cx - K / 2 * scale,
               cx + K / 2 * scale, 'K=%s  %d-φ%s' % (
                   row.get('D1', ''), n, row.get('d', '') or row.get('dta', '')))

    _centers(painter, [((cx, cy - ht - 25), (cx, cy + ht + 25))])
    _dim_h(painter, cy - ht - 50, cx - ro, cx + ro, 'D=%s' % row.get('D', ''))
    _dim_h(painter, cy + ht + 50, cx - ri, cx + ri, 'D4=%s' % row.get('D4', ''))
    _dim_v(painter, cx + ro + 50, cy - ht, cy + ht, 'H=%s' % row.get('H', ''))
    _text(painter, 24, 18, '容器法兰 NB/T 47023', 18, INK, Qt.AlignLeft, 700)
    _text(painter, 24, 46, 'DN %s  PN %s' % (row.get('DN', ''), row.get('PN', '')),
          14, QColor('#333'), Qt.AlignLeft, 700)
    painter.end()
    return pixmap

def _pipe_wall(row):
    for key in ('壁厚S(mm)', 'S', 'S_min', 'Sch40', 'STD', 'Sch80',
                'Sch10s', 'Sch5s', 'PN25', 'PN40'):
        value = _f(row, key)
        if value > 0:
            return value
    return 2.0


def render_pipe(row, tpl='pipe.bmp', width=800, height=500):
    od = _num(row, ('D_o', 'D_o_A'))
    wall = _pipe_wall(row)
    if od <= 0:
        return None
    idia = max(1.0, od - 2 * wall)
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.white)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    scale = min((width - 260) / od, (height - 220) / od)
    cx, cy = width / 2, height / 2
    ro, ri = od / 2 * scale, idia / 2 * scale
    painter.setBrush(FILL)
    painter.setPen(QPen(INK, 2.2))
    painter.drawEllipse(QPointF(cx, cy), ro, ro)
    painter.setBrush(Qt.white)
    painter.setPen(QPen(INK, 2.2))
    painter.drawEllipse(QPointF(cx, cy), ri, ri)
    _centers(painter, [
        (QPointF(cx - ro - 20, cy), QPointF(cx + ro + 20, cy)),
        (QPointF(cx, cy - ro - 20), QPointF(cx, cy + ro + 20))])
    _dim_h(painter, cy - ro - 55, cx - ro, cx + ro, 'D=%s' % row.get('D_o', ''))
    _dim_v(painter, cx + ro * 0.72, cy - ro, cy - ri, 'S=%g' % wall)
    _text(painter, 24, 18, '钢管 DN%s / %s' % (row.get('DN', ''), row.get('DN2', '')), 18, INK,
          Qt.AlignLeft, 600)
    _text(painter, 24, 46, 'DN %s  D_o %s  S %s mm' % (
        row.get('DN', ''), row.get('D_o', ''), ('%g' % wall)), 14,
        QColor('#333'), Qt.AlignLeft, 700)
    painter.end()
    return pixmap


def render_fitting(row, tpl='fittings_elbow.bmp', width=800, height=500,
                   angle=90, wall_series='Sch40'):
    """管件正投影：外轮廓实线、内孔虚线、图形自动居中。"""
    od = _num(row, ('D_o_A', 'D_o'))
    if od <= 0:
        return None
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.white)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    scale = min(300 / od, 2.0)
    wall_mm = wall_for(row, wall_series)
    wall = max(2.0, wall_mm * scale) if wall_mm > 0 else max(4.0, od * 0.08 * scale)

    def centered(path, dashed=None, centers=(), caps=(), center_path=None,
                 extra=None):
        box = path.boundingRect()
        if dashed is not None:
            box = path.united(dashed).boundingRect()
        if center_path is not None:
            box = box.united(center_path.boundingRect())
        dx = width / 2 - box.center().x()
        dy = height / 2 - box.center().y()
        painter.save()
        painter.translate(dx, dy)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(INK, 2.2))
        painter.drawPath(path)
        if dashed is not None:
            pen = QPen(INK, 1.2, Qt.DashLine)
            painter.setPen(pen)
            painter.drawPath(dashed)
        for p1, p2 in centers:
            painter.setPen(QPen(CENTER, 1.5, Qt.DashDotLine))
            painter.drawLine(p1, p2)
        if center_path is not None:
            pen = QPen(CENTER, 1.7, Qt.DashDotLine)
            pen.setDashPattern([12, 4, 3, 4])
            painter.setPen(pen)
            painter.drawPath(center_path)
        painter.setPen(QPen(INK, 2.2))
        for p1, p2 in caps:
            painter.drawLine(p1, p2)
        if extra is not None:
            extra()
        painter.restore()

    if 'elbow' in tpl:
        angle = int(angle)
        if angle == 45:
            h_val = _num(row, ('H_45',), od * 1.1)
        elif angle == 180:
            h_val = _num(row, ('A_180LR', 'P_180LR'), od * 2.0)
        else:
            h_val = _num(row, ('F_90LR', 'F_90SR'), od * 1.5)
        r_mm = od * 1.5
        scale = min(300 / max(od, h_val, r_mm), 4.0)
        R = max(40.0, r_mm * scale)
        ro, ri = R + od / 2 * scale, max(16.0, R - od / 2 * scale)
        span = math.radians(angle)
        po, pi = [], []
        steps = max(12, int(angle / 3))
        for k in range(steps + 1):
            th = math.pi + span * k / steps
            po.append(QPointF(ro * math.cos(th), ro * math.sin(th)))
            pi.append(QPointF(ri * math.cos(th), ri * math.sin(th)))
        outer = QPainterPath()
        outer.moveTo(po[0])
        for q in po[1:]:
            outer.lineTo(q)
        inner_arc = QPainterPath()
        inner_arc.moveTo(pi[0])
        for q in pi[1:]:
            inner_arc.lineTo(q)
        # 正投影：外弧/端面实线，内孔弧虚线，中心线沿弯曲方向
        mid_a = math.pi + span / 2
        center_arc = QPainterPath()
        center_arc.moveTo(QPointF(R * math.cos(math.pi),
                                  R * math.sin(math.pi)))
        for k in range(1, steps + 1):
            th = math.pi + span * k / steps
            center_arc.lineTo(QPointF(R * math.cos(th), R * math.sin(th)))

        def elbow_dims():
            painter.setPen(QPen(DIM, 1.2))
            midp = QPointF(R * math.cos(mid_a), R * math.sin(mid_a))
            _arrow(painter, QPointF(0, 0), midp, 7)
            _text(painter, midp.x() - 40, midp.y() - 20,
                  'R=%g' % r_mm, 14, DIM, Qt.AlignHCenter, 100, True)
            _arrow(painter, po[-1], pi[-1], 7)
            _text(painter, po[-1].x() + 8, po[-1].y() - 8,
                  'D=%s' % row.get('D_o_A', ''), 14, DIM, Qt.AlignLeft, 120,
                  True)
            endp = QPointF((po[-1].x() + pi[-1].x()) / 2,
                           (po[-1].y() + pi[-1].y()) / 2)
            _arrow(painter, QPointF(0, 0), endp, 7)
            _text(painter, endp.x() + 8, endp.y() + 12,
                  'H=%g' % h_val, 14, DIM, Qt.AlignLeft, 120, True)
            _text(painter, -60, -R - 18, '%d°' % angle, 15, DIM,
                  Qt.AlignHCenter, 120, True)

        centered(outer, inner_arc, (), [(po[0], pi[0]), (po[-1], pi[-1])],
                 center_arc, elbow_dims)
        _text(painter, 24, 18, '%s°弯头 %s' % (angle, row.get('DN2', '')), 18,
              INK, Qt.AlignLeft, 600)
        _text(painter, 24, 46, 'R=%g  H=%g  D=%s' % (
            r_mm, h_val, row.get('D_o_A', '')), 14, QColor('#333'))
    elif 'tee' in tpl:
        c = _num(row, ('C',), od * 1.2)
        w = max(80.0, c * scale)
        half = od / 2 * scale
        outer = QPainterPath()
        outer.addRect(QRectF(-w, -half, 2 * w, 2 * half))
        branch = QPainterPath()
        branch.addRect(QRectF(-half, -w, 2 * half, w))
        outer = outer.united(branch)
        iw = max(4.0, half - wall)
        inner = QPainterPath()
        inner.addRect(QRectF(-w + wall, -iw, 2 * (w - wall), 2 * iw))
        ib = QPainterPath()
        ib.addRect(QRectF(-iw, -w + wall, 2 * iw, w - wall))
        inner = inner.united(ib)
        def tee_dims():
            _dim_h(painter, half + 28, -w, w, 'C=%s' % row.get('C', ''), 14)
            _text(painter, -w, -half - 34, 'D=%s' % row.get('D_o_A', ''),
                  14, DIM, Qt.AlignLeft, 160)

        centered(outer, inner,
                 [(QPointF(-w, 0), QPointF(w, 0)),
                  (QPointF(0, -w), QPointF(0, 0))], extra=tee_dims)
        _text(painter, 24, 18, '等径三通 %s' % row.get('DN2', ''), 18, INK,
              Qt.AlignLeft, 600)
        _text(painter, 24, 46, 'C=%s  D=%s' % (
            row.get('C', ''), row.get('D_o_A', '')), 14, QColor('#333'))
    elif 'reducer' in tpl:
        r1 = od / 2 * scale
        r2 = max(6.0, _num(row, ('D_o_B',), od * 0.7) / 2 * scale)
        h = max(100.0, min(220.0, _num(row, ('H',), 100) * 0.9))
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
        def reducer_dims():
            _dim_v(painter, r1 + 28, -h / 2, h / 2,
                   'H=%s' % row.get('H', ''), 14)
            _text(painter, -r1, -h / 2 - 34,
                  'D1=%s  D2=%s' % (row.get('D_o_A', ''),
                                    row.get('D_o_B', '')),
                  14, DIM, Qt.AlignLeft, 220)

        centered(outer, inner, [(QPointF(0, -h / 2 - 20),
                                 QPointF(0, h / 2 + 20))], extra=reducer_dims)
        _text(painter, 24, 18, '异径管 %s' % row.get('DN2', ''), 18, INK,
              Qt.AlignLeft, 600)
        _text(painter, 24, 46, 'D1=%s  D2=%s  H=%s' % (
            row.get('D_o_A', ''), row.get('D_o_B', ''), row.get('H', '')),
            14, QColor('#333'))
    else:
        r = od / 2 * scale
        outer = QPainterPath()
        outer.moveTo(-r, 0)
        outer.arcTo(QRectF(-r, -r, 2 * r, 2 * r), 180, -180)
        outer.closeSubpath()
        inner = QPainterPath()
        inner.moveTo(-max(2, r - wall), 0)
        inner.arcTo(QRectF(-max(2, r - wall), -max(2, r - wall),
                           2 * max(2, r - wall), 2 * max(2, r - wall)),
                    180, -180)
        inner.closeSubpath()
        def cap_dims():
            _dim_h(painter, -r - 28, -r, r,
                   'D=%s' % row.get('D_o_A', ''), 14)
            _text(painter, -r, r + 8, 'E=%s' % row.get('E', ''),
                  14, DIM, Qt.AlignLeft, 160)

        centered(outer, inner, [(QPointF(-r - 20, 0), QPointF(r + 20, 0))],
                 extra=cap_dims)
        _text(painter, 24, 18, '椭圆管帽 %s' % row.get('DN2', ''), 18, INK,
              Qt.AlignLeft, 600)
        _text(painter, 24, 46, 'E=%s  D=%s' % (
            row.get('E', ''), row.get('D_o_A', '')), 14, QColor('#333'))
    painter.end()
    return pixmap


def render_seal(row, tpl='mfm_突面.bmp', width=800, height=500):
    """密封面沟槽剖面示意：RF / MFM / TG / RJ。"""
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.white)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    cx, cy = width / 2, height / 2
    plate_w, plate_h, gap = 500, 58, 26
    upper = QRectF(cx - plate_w / 2, cy - gap / 2 - plate_h, plate_w, plate_h)
    lower = QRectF(cx - plate_w / 2, cy + gap / 2, plate_w, plate_h)
    painter.setBrush(FILL)
    painter.setPen(QPen(INK, 2.0))
    painter.drawRect(upper)
    painter.drawRect(lower)

    painter.setPen(QPen(INK, 1.6))
    name = row.get('名称', '') or row.get('代号', '')
    if '环连接' in tpl or 'RJ' in tpl:
        # 上下各一个八角沟槽
        for yy in (upper.bottom() - 6, lower.top() + 6):
            poly = QPolygonF([
                QPointF(cx - 120, yy + 8), QPointF(cx - 80, yy - 14),
                QPointF(cx + 80, yy - 14), QPointF(cx + 120, yy + 8),
                QPointF(cx + 80, yy + 22), QPointF(cx - 80, yy + 22),
            ])
            painter.drawPolygon(poly)
            _text(painter, cx - 80, yy - 4, '八角槽', 12, DIM,
                  Qt.AlignHCenter, 160, True)
    elif '凹凸' in tpl or 'MFM' in tpl:
        # 上凹槽、下凸榫
        groove = QRectF(cx - 90, upper.bottom() - 16, 180, 16)
        painter.setBrush(Qt.white)
        painter.drawRect(groove)
        painter.setBrush(FILL)
        painter.drawRect(QRectF(cx - 80, lower.top() - 14, 160, 14))
        _text(painter, cx - 100, upper.top() + 5, '凹槽', 12, DIM,
              Qt.AlignHCenter, 200, True)
        _text(painter, cx - 100, lower.bottom() - 20, '凸榫', 12, DIM,
              Qt.AlignHCenter, 200, True)
    elif '榫槽' in tpl or 'TG' in tpl:
        # 上凸榫、下凹槽
        painter.setBrush(FILL)
        painter.drawRect(QRectF(cx - 80, upper.bottom() - 14, 160, 14))
        painter.setBrush(Qt.white)
        painter.drawRect(QRectF(cx - 90, lower.top(), 180, 16))
        _text(painter, cx - 100, upper.top() + 5, '凸榫', 12, DIM,
              Qt.AlignHCenter, 200, True)
        _text(painter, cx - 100, lower.bottom() - 20, '凹槽', 12, DIM,
              Qt.AlignHCenter, 200, True)
    else:
        # RF：上突面、下平面
        painter.setBrush(FILL)
        painter.drawRect(QRectF(cx - 180, upper.bottom() - 12, 360, 12))
        _text(painter, cx - 100, upper.top() + 5, '突面', 12, DIM,
              Qt.AlignHCenter, 200, True)
        painter.drawLine(QPointF(cx - 250, lower.top()),
                         QPointF(cx + 250, lower.top()))

    _centers(painter, [((cx, upper.top() - 20), (cx, lower.bottom() + 20))])
    _text(painter, 24, 18, '密封面 %s %s' % (row.get('代号', ''), name),
          18, INK, Qt.AlignLeft, 700)
    _text(painter, 24, 46, '沟槽剖面示意  %s' % row.get('适用压力范围', ''),
          14, QColor('#333'), Qt.AlignLeft, 700)
    painter.end()
    return pixmap
