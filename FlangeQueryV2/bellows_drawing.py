# -*- coding: utf-8 -*-
"""U 形波纹伸缩节参数化矢量剖面（验证实现）。"""

import math
import re

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import (QColor, QFont, QFontMetrics, QPainter, QPainterPath,
                         QPen, QPixmap, QPolygonF)

INK = QColor('#d02020')
FILL = QColor('#fff5f5')
TEXT = QColor('#333333')
DIM = QColor('#7a8794')
_SHOW_LABELS = True


def _f(value, default=0.0):
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def pipeline(row):
    spec = str(row.get('接管规格', '') or '')
    m = re.search(r'([\d.]+)\s*[×xX]\s*([\d.]+)', spec)
    od = _f(m.group(1)) if m else _f(row.get('D_o'))
    wall = _f(m.group(2), 3.0) if m else 3.0
    return spec, od, wall


def _arrow(painter, p1, p2, size=6):
    painter.drawLine(p1, p2)

    def head(tip, other):
        dx, dy = tip.x() - other.x(), tip.y() - other.y()
        length = math.hypot(dx, dy) or 1.0
        ux, uy = dx / length, dy / length
        bx, by = tip.x() - ux * size, tip.y() - uy * size
        painter.drawLine(tip, QPointF(bx - uy * size * 0.45,
                                      by + ux * size * 0.45))
        painter.drawLine(tip, QPointF(bx + uy * size * 0.45,
                                      by - ux * size * 0.45))

    head(p2, p1)
    head(p1, p2)


def _text(painter, x, y, text, size=12, color=TEXT, align=Qt.AlignLeft,
          width=240, bg=False):
    if not _SHOW_LABELS:
        return
    font = QFont('Microsoft YaHei')
    font.setPixelSize(size)
    painter.setFont(font)
    painter.setPen(color)
    rect = QRectF(x, y, width, size + 8)
    if bg:
        metrics = QFontMetrics(font)
        tw = metrics.horizontalAdvance(text)
        if align & Qt.AlignRight:
            bx = x + width - tw
        elif align & Qt.AlignHCenter:
            bx = x + (width - tw) / 2
        else:
            bx = x
        painter.fillRect(QRectF(bx - 3, y - 1, tw + 6, size + 8), Qt.white)
    painter.drawText(rect, align | Qt.AlignVCenter, text)


def _smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _arc_points(cx, cy, radius, a0, a1, steps=10):
    pts = []
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * i / steps
        pts.append((cx + radius * math.cos(a),
                    cy + radius * math.sin(a)))
    return pts


def _wave_points(q, h, r):
    """一个波的解析轮廓：波谷/波峰圆弧与公切直边，返回 (x, y)。"""
    q = max(q, 0.1)
    h = max(h, 0.1)
    r = max(0.05, min(r, q / 4.2, h / 2.1))
    half = q / 2.0
    a, b = half, h - 2 * r
    dist = math.hypot(a, b)
    total_r = 2 * r
    if dist <= total_r + 1e-6:
        r = min(q / 4.2, h / 2.2)
        b = h - 2 * r
        dist = math.hypot(a, b)
        total_r = 2 * r
    root_len = math.sqrt(max(0.0, dist * dist - total_r * total_r))
    nx = (total_r * a + root_len * b) / (dist * dist)
    ny = (total_r * b - root_len * a) / (dist * dist)
    t0 = (r * nx, r + r * ny)
    t1 = (half - r * nx, h - r - r * ny)
    alpha = math.atan2(t0[1] - r, t0[0])
    beta = math.atan2(t1[1] - (h - r), t1[0] - half)
    t0m = (q - t0[0], t0[1])
    t1m = (q - t1[0], t1[1])
    pts = [(0.0, 0.0)]
    pts += _arc_points(0, r, r, -math.pi / 2, alpha)[1:]
    pts.append(t1)
    pts += _arc_points(half, h - r, r, beta, math.pi / 2)[1:]
    pts += _arc_points(half, h - r, r, math.pi / 2, math.pi - beta)[1:]
    pts.append(t0m)
    pts += _arc_points(q, r, r, math.pi - alpha,
                       3 * math.pi / 2)[1:]
    pts.append((q, 0.0))
    return pts

def _draw_frame(painter, width, height, row):
    """A3 图框 + 右下角标题栏。"""
    margin, inner = 18, 26
    painter.setPen(QPen(QColor('#333333'), 1.5))
    painter.setBrush(Qt.NoBrush)
    painter.drawRect(QRectF(8, 8, width - 16, height - 16))
    painter.setPen(QPen(QColor('#333333'), 1))
    painter.drawRect(QRectF(margin, margin, width - 2 * margin,
                             height - 2 * margin))
    bw, bh = 360, 108
    bx, by = width - margin - bw, height - margin - bh
    painter.setBrush(Qt.white)
    painter.setPen(QPen(QColor('#333333'), 1.2))
    painter.drawRect(QRectF(bx, by, bw, bh))
    for i in (28, 50, 70, 90):
        painter.drawLine(QPointF(bx, by + i), QPointF(bx + bw, by + i))
    painter.drawLine(QPointF(bx + 205, by + 50), QPointF(bx + 205, by + 90))
    dn = str(row.get('DN', ''))
    rows = [
        ('U 形波纹伸缩节', '图号 U-DN%s' % dn),
        ('标准 70B125-2002', '规格 DN%s' % dn),
        ('端部 焊接坡口 30°', '材料 待定'),
        ('比例 示意（按真实尺寸）', '日期 2026-10-24'),
        ('设计', '审核'),
    ]
    for i, (left, right) in enumerate(rows):
        y = by + i * 20 + 4
        _text(painter, bx + 6, y, left, 10, QColor('#222222'))
        if i < 3:
            _text(painter, bx + 210, y, right, 10, QColor('#222222'))
        elif i == 3:
            _text(painter, bx + 210, y, right, 10, QColor('#222222'))
    _text(painter, bx + 210, by + 92, '第1页 共1页', 9, QColor('#222222'))

def render_bellows(row, width=1200, height=760, show_labels=True, inset=True,
                  frame=False):
    global _SHOW_LABELS
    _old_labels = _SHOW_LABELS
    _SHOW_LABELS = show_labels
    """按 U_bellows 几何参数绘制真实比例剖面。"""
    spec, pipe_od, wall = pipeline(row)
    dn = str(row.get('DN', '') or '')
    d_o = _f(row.get('D_o'), pipe_od)
    h = _f(row.get('h'), 8)
    q = _f(row.get('q'), 8)
    r = _f(row.get('r'), 1.5)
    lt = _f(row.get('Lt'), 15)
    n = max(1, int(_f(row.get('N'), 4)))
    a = _f(row.get('a'), 0)

    root_r = d_o / 2.0
    crest_r = root_r + h
    pipe_r = pipe_od / 2.0
    total_l = 2 * lt + n * q
    max_r = max(pipe_r, crest_r)
    margin_x, margin_y = 150, 120
    scale = min((width - 2 * margin_x) / max(total_l, 1),
                (height - 2 * margin_y) / max(2 * max_r, 1))
    x0 = (width - total_l * scale) / 2
    cy = height / 2 + 18

    def X(mm):
        return x0 + mm * scale

    def Y(radius):
        return cy - radius * scale

    wave = _wave_points(q, h, r)
    bevel = max(2.0, wall * 1.87)  # 30° 坡口：径向 0.5δ / tan15°
    end_r = max(wall, pipe_r - wall * 0.5)
    top_mm = [(0.0, end_r), (bevel, pipe_r), (lt, pipe_r)]
    if abs(pipe_r - root_r) > 1e-6:
        top_mm.append((lt, root_r))
    for i in range(n):
        for wx, wy in wave:
            top_mm.append((lt + i * q + wx, root_r + wy))
    if abs(pipe_r - root_r) > 1e-6:
        top_mm.append((lt + n * q, pipe_r))
    top_mm.append((total_l - bevel, pipe_r))
    top_mm.append((total_l, end_r))
    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.white)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)

    # 中心线
    pen = QPen(QColor('#9aa7b4'), 1, Qt.DashDotLine)
    painter.setPen(pen)
    painter.drawLine(QPointF(30, cy), QPointF(width - 30, cy))

    # 外轮廓 / 内轮廓
    wb = max(1.0, wall * 0.45)
    outer = [(X(x), Y(y)) for x, y in top_mm]
    inner = [(X(x), Y(y - wb)) for x, y in top_mm]
    path = QPainterPath()
    path.moveTo(QPointF(X(0), Y(top_mm[0][1])))
    for px, py in outer:
        path.lineTo(px, py)
    path.lineTo(QPointF(X(total_l), Y(-top_mm[-1][1])))
    for x, y in reversed(top_mm):
        path.lineTo(QPointF(X(x), Y(-y)))
    path.lineTo(QPointF(X(0), Y(-top_mm[0][1])))
    path.closeSubpath()
    painter.setBrush(FILL)
    painter.setPen(QPen(INK, 2))
    painter.drawPath(path)

    inner_path = QPainterPath()
    inner_path.moveTo(QPointF(X(0), Y(top_mm[0][1] - wb)))
    for px, py in inner:
        inner_path.lineTo(px, py)
    inner_path.lineTo(QPointF(X(total_l), Y(-(top_mm[-1][1] - wb))))
    for x, y in reversed(top_mm):
        inner_path.lineTo(QPointF(X(x), Y(-(y - wb))))
    inner_path.lineTo(QPointF(X(0), Y(-(top_mm[0][1] - wb))))
    inner_path.closeSubpath()
    painter.setBrush(Qt.white)
    painter.setPen(QPen(INK, 1.2))
    painter.drawPath(inner_path)

    # 剖面线（金属壁）
    wall_path = path.subtracted(inner_path)
    painter.save()
    painter.setClipPath(wall_path)
    painter.setPen(QPen(QColor('#e6a3a3'), 1))
    rect = path.boundingRect()
    step = 8
    x = rect.left() - rect.height()
    while x < rect.right() + rect.height():
        painter.drawLine(QPointF(x, rect.bottom()),
                         QPointF(x + rect.height(), rect.top()))
        x += step
    painter.restore()
    painter.setBrush(Qt.NoBrush)
    painter.setPen(QPen(INK, 2))
    painter.drawPath(path)
    painter.setPen(QPen(QColor('#222222'), 1.2))
    painter.drawPath(inner_path)

    # 波谷内衬线（参考图中的黑色竖线）
    painter.setPen(QPen(QColor('#222222'), 1.2))
    for i in range(n):
        vx = X(lt + (i + 0.5) * q)
        painter.drawLine(QPointF(vx, Y(root_r - wb)),
                         QPointF(vx, Y(-(root_r - wb))))

    # 焊接端坡口（30°）
    painter.setPen(QPen(INK, 2))
    painter.drawLine(QPointF(X(0), Y(end_r)), QPointF(X(0), Y(-end_r)))
    painter.drawLine(QPointF(X(total_l), Y(end_r)),
                     QPointF(X(total_l), Y(-end_r)))
    painter.setPen(QPen(DIM, 1))
    painter.drawLine(QPointF(X(0), Y(end_r)), QPointF(X(bevel), Y(pipe_r)))
    painter.drawLine(QPointF(X(total_l), Y(-end_r)),
                     QPointF(X(total_l - bevel), Y(-pipe_r)))

    # 标题
    _text(painter, 28, 18, 'U 形波纹伸缩节 · DN%s' % dn, 20, INK)
    _text(painter, 28, 46, '接管 %s  ·  N=%d 波  ·  比例按真实尺寸' %
          (spec or 'φ%s×%s' % (pipe_od, wall), n), 12, TEXT,
          Qt.AlignLeft, 520)
    _text(painter, width - 300, 18, '接管 %s' % (spec or '—'), 14, INK,
          Qt.AlignRight)

    # D_o 直径尺寸（管端左侧）
    draw_w = total_l * scale
    narrow = draw_w < 520
    dx = X(0) - 46
    painter.setPen(QPen(DIM, 1))
    painter.drawLine(QPointF(X(lt), Y(root_r)), QPointF(dx, Y(root_r)))
    painter.drawLine(QPointF(X(lt), Y(-root_r)), QPointF(dx, Y(-root_r)))
    _arrow(painter, QPointF(dx, Y(root_r)), QPointF(dx, Y(-root_r)))
    _text(painter, dx - 226, cy - 8, 'D₀=%s' % row.get('D_o', ''), 12, DIM,
          Qt.AlignRight, 220, True)

    if narrow:
        # 大直径产品真实比例下很窄，尺寸集中到右侧图例，避免压线。
        lx = max(X(total_l) + 50, 640)
        ly = 150
        _text(painter, lx, ly, '尺寸参数', 14, INK)
        items = [
            'N = %d 波' % n,
            'q = %s mm' % row.get('q', ''),
            'h = %s mm' % row.get('h', ''),
            'r = %s mm' % row.get('r', ''),
            'Lt = %s mm' % row.get('Lt', ''),
            'a = %s mm' % row.get('a', ''),
            'L = %d mm' % (2 * lt + n * q),
        ]
        for i, line in enumerate(items):
            _text(painter, lx, ly + 32 + i * 28, line, 13, TEXT)
        _text(painter, 28, height - 72,
              '注：大直径按真实比例，建议配局部放大图使用。', 12, DIM)
    else:
        # h 波高（中间波峰，避免与 q 重叠）
        peak_mm = lt + q * (n / 2.0 + 0.5)
        peak_x = X(peak_mm)
        painter.setPen(QPen(DIM, 1))
        _arrow(painter, QPointF(peak_x, Y(root_r)),
               QPointF(peak_x, Y(crest_r)))
        _text(painter, peak_x - 28, Y(crest_r) - 26,
              'h=%s' % row.get('h', ''), 12, DIM, Qt.AlignHCenter, 70, True)

        # q 波距（首两个波峰）
        x1 = X(lt + q * 0.5)
        x2 = X(lt + q * 1.5)
        yq = Y(crest_r) - 46
        painter.setPen(QPen(DIM, 1))
        _arrow(painter, QPointF(x1, yq), QPointF(x2, yq))
        painter.drawLine(QPointF(x1, Y(crest_r)), QPointF(x1, yq))
        painter.drawLine(QPointF(x2, Y(crest_r)), QPointF(x2, yq))
        _text(painter, (x1 + x2) / 2 - 45, yq - 24,
              'q=%s' % row.get('q', ''), 12, DIM, Qt.AlignHCenter, 90, True)

        # Lt 直段（左下）
        yl = Y(-max_r) + 30
        painter.setPen(QPen(DIM, 1))
        _arrow(painter, QPointF(X(0), yl), QPointF(X(lt), yl))
        painter.drawLine(QPointF(X(0), Y(-pipe_r)), QPointF(X(0), yl))
        painter.drawLine(QPointF(X(lt), Y(-root_r)), QPointF(X(lt), yl))
        _text(painter, X(0) - 10, yl + 10, 'Lt=%s' % row.get('Lt', ''), 12,
              DIM, Qt.AlignLeft, 100, True)

        # r 波谷圆角（右下）
        rx = X(lt + n * q - 0.12 * q)
        ry = Y(-root_r)
        painter.setPen(QPen(DIM, 1))
        painter.drawLine(QPointF(rx, ry), QPointF(rx + 26, ry + 42))
        _text(painter, rx + 28, ry + 42, 'r=%s' % row.get('r', ''), 12, DIM,
              Qt.AlignLeft, 100, True)

        # 总长 L（底部）
        yl2 = height - 84
        painter.setPen(QPen(DIM, 1))
        _arrow(painter, QPointF(X(0), yl2), QPointF(X(total_l), yl2))
        painter.drawLine(QPointF(X(0), Y(-pipe_r)), QPointF(X(0), yl2))
        painter.drawLine(QPointF(X(total_l), Y(-pipe_r)),
                         QPointF(X(total_l), yl2))
        _text(painter, width / 2 - 90, yl2 - 22,
              'L=%d mm' % (2 * lt + n * q), 12, DIM,
              Qt.AlignHCenter, 180, True)

        # N / a（下方）
        _text(painter, width / 2 - 240, height - 48,
              'N=%d 波   a=%s mm' % (n, row.get('a', '')), 13, TEXT,
              Qt.AlignHCenter, 480)

    if inset and narrow:
        # 大直径真实比例过窄：右下角 3 波局部放大，左右用断裂线表示断开
        src = QRectF(X(lt), Y(crest_r) - 6,
                     max(18.0, 3 * q * scale),
                     max(18.0, (h + wall * 2) * scale))
        src = src.intersected(QRectF(pixmap.rect()))
        detail = pixmap.copy(src.toRect()).scaled(
            340, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        dx, dy = width - 390, height - 230
        painter.drawPixmap(dx, dy, detail)
        painter.setPen(QPen(DIM, 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawLine(QPointF(dx, dy), QPointF(dx + 342, dy))
        painter.drawLine(QPointF(dx, dy + 162), QPointF(dx + 342, dy + 162))
        for bx in (dx, dx + 342):
            path = QPainterPath()
            path.moveTo(bx, dy)
            for i in range(1, 11):
                y = dy + i * 16.2
                path.lineTo(bx + (6 if i % 2 else -6), y)
            painter.drawPath(path)
        _text(painter, dx, dy - 24, '局部放大（断开视图）', 11, DIM)
    if frame:
        _draw_frame(painter, width, height, row)
    painter.end()
    _SHOW_LABELS = _old_labels
    return pixmap


def compact_labels(row):
    """侧栏只保留 DN；其余尺寸由 KV 列表展示，PDF 用完整标签。"""
    return {
        'dn': ((24, 12, 500, 30), 'DN {DN}'),
    }