# -*- coding: utf-8 -*-
"""参数化法兰剖面图（QPainter 矢量），替代 WN 页的位图 + 固定坐标标注。

只负责几何与尺寸线绘制，不依赖主窗口；尺寸缺失时返回 None，调用方回退到 BMP。
"""

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import (QBrush, QColor, QFont, QPainter, QPen, QPixmap,
                         QPolygonF)

INK = QColor('#1a1a1a')
CENTER = QColor('#8a8f98')
FILL = QColor('#dbe6f2')


def _num(row, key, default=None):
    value = str(row.get(key, '')).strip()
    if value in ('', '-'):
        return default
    try:
        return float(value.replace(',', '.'))
    except ValueError:
        return default


def _dims(row):
    D = _num(row, 'D')
    d = _num(row, 'd') or _num(row, 'RF_d')
    C = _num(row, 'C')
    H = _num(row, 'H')
    if not all(v and v > 0 for v in (D, d, C, H)):
        return None
    rf = _num(row, 'RF_d', D) or D
    f1 = _num(row, 'RF_f1', 2) or 2
    N = _num(row, 'N_A') or _num(row, 'N_B') or d
    A1 = _num(row, 'A1_A') or _num(row, 'A1_B') or d
    return {
        'D': D, 'd': min(d, D * 0.9), 'C': C, 'H': H,
        'rf': max(d, min(rf, D)),
        'f1': max(0.0, min(f1, C)),
        'N': max(d, min(N, D * 0.95)),
        'A1': max(d * 0.95, min(A1, D * 0.95)),
        'K': _num(row, 'K'), 'L': _num(row, 'L'), 'n': _num(row, 'n'),
        'hub': max(H, C + f1 + 2),
    }


def render_flange(row, width=596, height=498):
    """按行数据绘制法兰全剖立面，返回 QPixmap；尺寸不足返回 None。"""
    dims = _dims(row)
    if dims is None:
        return None

    D, d, C, H = dims['D'], dims['d'], dims['C'], dims['H']
    rf, f1 = dims['rf'], dims['f1']
    N, A1, hub = dims['N'], dims['A1'], dims['hub']
    K, L, bolt_n = dims['K'], dims['L'], dims['n']

    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.white)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)

    margin_l, margin_r, margin_t, margin_b = 72, 96, 26, 30
    avail_w = width - margin_l - margin_r
    avail_h = height - margin_t - margin_b
    scale = min(avail_w / (D * 1.16), avail_h / (hub * 1.2))
    if scale <= 0:
        painter.end()
        return None
    ox = margin_l + avail_w / 2.0
    oy = margin_t + (avail_h - hub * scale) / 2.0 + 4

    painter.translate(ox, oy)
    painter.scale(scale, scale)

    pen_w = max(0.7, 1.35 / scale)
    ink_pen = QPen(INK, pen_w)
    ink_pen.setJoinStyle(Qt.RoundJoin)

    disc_bottom = f1 + C
    half = [
        (d / 2.0, 0.0), (rf / 2.0, 0.0), (rf / 2.0, f1),
        (D / 2.0, f1), (D / 2.0, disc_bottom), (N / 2.0, disc_bottom),
        (A1 / 2.0, hub), (d / 2.0, hub),
    ]

    def polygon(points):
        return QPolygonF([QPointF(x, y) for x, y in points])

    brush = QBrush(FILL, Qt.BDiagPattern)
    for sign in (1, -1):
        pts = [(sign * x, y) for x, y in half]
        painter.setPen(ink_pen)
        painter.setBrush(brush)
        painter.drawPolygon(polygon(pts))

    # 螺栓孔：剖面上画成白色圆孔
    if K and L and L > 0:
        hole_r = min(L / 2.0, D * 0.08)
        painter.setBrush(QBrush(Qt.white))
        painter.setPen(QPen(INK, pen_w * 0.8))
        for cx in (-K / 2.0, K / 2.0):
            painter.drawEllipse(QPointF(cx, f1 + C / 2.0), hole_r, hole_r)

    # 中心线
    center_pen = QPen(CENTER, max(0.5, 0.8 / scale), Qt.DashDotLine)
    painter.setPen(center_pen)
    painter.setBrush(Qt.NoBrush)
    painter.drawLine(QPointF(0, -hub * 0.12), QPointF(0, hub * 1.06))

    font = QFont('Microsoft YaHei')
    font.setPixelSize(max(8, int(11 / scale)))

    def label(x, y, text, align=Qt.AlignCenter):
        painter.setFont(font)
        painter.setPen(INK)
        width_mm = max(12.0, len(text) * 3.2)
        rect = QRectF(x - width_mm / 2.0, y - 4.0, width_mm, 8.0)
        painter.drawText(rect, align | Qt.AlignVCenter, text)

    def hdim(y, left, right, text, offset=0.0):
        painter.setPen(QPen(INK, max(0.5, 0.8 / scale)))
        painter.setBrush(Qt.NoBrush)
        painter.drawLine(QPointF(left, y), QPointF(right, y))
        tick = max(1.2, 2.2 / scale)
        painter.drawLine(QPointF(left, y - tick), QPointF(left, y + tick))
        painter.drawLine(QPointF(right, y - tick), QPointF(right, y + tick))
        label((left + right) / 2.0, y + offset + 5.5, text)

    def vdim(x, top, bottom, text):
        painter.setPen(QPen(INK, max(0.5, 0.8 / scale)))
        painter.setBrush(Qt.NoBrush)
        painter.drawLine(QPointF(x, top), QPointF(x, bottom))
        tick = max(1.2, 2.2 / scale)
        painter.drawLine(QPointF(x - tick, top), QPointF(x + tick, top))
        painter.drawLine(QPointF(x - tick, bottom), QPointF(x + tick, bottom))
        label(x + 2.0, (top + bottom) / 2.0, text, Qt.AlignLeft)

    hdim(disc_bottom + 10.0, -D / 2.0, D / 2.0, 'D=%g' % D)
    if K:
        hdim(disc_bottom + 4.0, -K / 2.0, K / 2.0, 'K=%g' % K)
    vdim(D / 2.0 + 6.0, f1, disc_bottom, 'C=%g' % C)
    vdim(A1 / 2.0 + 10.0, 0.0, hub, 'H=%g' % hub)
    label(0.0, -5.0, 'd=%g' % (2 * d / 2.0))
    label(N / 2.0 + 3.0, disc_bottom + 1.0, 'N=%g' % N, Qt.AlignLeft)
    label(A1 / 2.0 + 3.0, hub - 2.0, 'A1=%g' % A1, Qt.AlignLeft)
    if K and L and bolt_n:
        label(-K / 2.0, f1 + C / 2.0 - min(L / 2.0, D * 0.08) - 3.0,
              '%g×Φ%g' % (bolt_n, L))

    painter.end()
    return pixmap
