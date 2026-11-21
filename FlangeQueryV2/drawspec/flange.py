# -*- coding: utf-8 -*-
"""法兰的法兰剖面 DrawingSpec 适配器（不依赖 QPixmap）。"""

from PyQt5.QtCore import QPointF, Qt
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


def _face_points(face, H, rf_f, rf_r, bore_r, pr):
    if face in ('RF', 'TG'):
        if rf_r >= pr - 0.5:
            return [(H, pr), (H, bore_r)]
        y0 = H - rf_f
        return [(y0, pr), (y0, rf_r), (H, rf_r), (H, bore_r)]
    if face in ('MFM', 'RJ'):
        if rf_r >= pr - 0.5:
            return [(H, pr), (H, bore_r)]
        y0 = H - rf_f
        return [(H, pr), (H, rf_r), (y0, rf_r), (y0, bore_r)]
    return [(H, pr), (H, bore_r)]


def build_flange_spec(row, kind='WN', face='RF', width=1200, height=900,
                      standard=''):
    D = _f(row, 'D')
    K = _f(row, 'K')
    L = _f(row, 'L')
    C = _f(row, 'C')
    H = _f(row, 'H')
    N = _f(row, 'N_A') or _f(row, 'N_B')
    A1 = _f(row, 'A1_A') or _f(row, 'A1_B')
    S = _f(row, 'S_min') or _f(row, 'S')
    n = int(_f(row, 'n', 4))
    try:
        dn = float(str(row.get('DN', '')).rstrip('aA'))
    except ValueError:
        dn = 0.0
    if kind == 'PJ':
        H = _f(row, 'h') or _f(row, 'H_d') or H
        N = _f(row, 'B1_A') or _f(row, 'B1_B') or N
    if kind in ('PL', 'BL'):
        H = C
    if kind == 'BL':
        A1, N, S = dn, dn, 0.0
    if A1 <= 0:
        A1 = dn + 6.0
    if N <= 0:
        N = A1
    if min(D, K, C, H, A1) <= 0:
        return None

    plate_r, hub_r, pipe_r = D / 2.0, N / 2.0, A1 / 2.0
    plate_start = 0.0 if kind in ('PL', 'BL') else max(0.0, H - C)
    bore = _f(row, 'd_bore')
    if kind == 'BL':
        bore = 0.0
    elif bore <= 0:
        bore = max(1.0, A1 - 2 * S)
    bore_r = bore / 2.0
    rf_d = _f(row, 'RF_d') or max(bore + 8, D * 0.62)
    rf_f = _f(row, 'RF_f1') or max(2, C * 0.08)
    rf_r = min(plate_r, max(bore_r + 0.5, rf_d / 2))
    rf_f = min(rf_f, max(1, H * 0.2))
    face = (face or 'RF').upper()

    left, top = 70, 220
    draw_w, draw_h = width - 380, height - 360
    scale = min(draw_w / max(D, 1), draw_h / max(H, 1))
    cx = width / 2.0

    def X(r):
        return cx + r * scale

    def Y(a):
        return top + a * scale

    if kind == 'BL':
        pts = [(0, 0), (0, plate_r), (H, plate_r), (H, 0)]
    elif kind == 'PL':
        pts = [(0, bore_r), (0, plate_r)] + _face_points(
            face, H, rf_f, rf_r, bore_r, plate_r)
    elif kind in ('SO', 'SW', 'TH', 'IF', 'PJ'):
        pts = [(0, bore_r), (0, hub_r), (plate_start, hub_r),
               (plate_start, plate_r)] + _face_points(
            face, H, rf_f, rf_r, bore_r, plate_r)
    else:
        pts = [(0, bore_r), (0, pipe_r), (plate_start, hub_r),
               (plate_start, plate_r)] + _face_points(
            face, H, rf_f, rf_r, bore_r, plate_r)

    path = QPainterPath()
    path.moveTo(X(pts[0][1]), Y(pts[0][0]))
    for a, r in pts:
        path.lineTo(X(r), Y(a))
    for a, r in reversed(pts):
        path.lineTo(X(-r), Y(a))
    path.closeSubpath()

    spec = DrawingSpec(
        title='%s  %s  DN%s  %s  %s' % (
            standard or ('GB/T 9124.2-2019' if row.get('Class')
                         else 'GB/T 9124.1-2019'),
            ('Class ' + row.get('Class', '')) if row.get('Class')
            else ('PN' + row.get('PN', '')),
            row.get('DN', ''), kind, face),
        width=width, height=height, source=standard)
    spec.path(path, QPen(INK, 2.2), FILL)

    # 螺栓孔
    for sign in (1, -1):
        x1 = X(sign * (K / 2 + L / 2))
        x2 = X(sign * (K / 2 - L / 2))
        p = QPainterPath()
        p.addRect(min(x1, x2), Y(plate_start), abs(x2 - x1), C * scale)
        spec.path(p, QPen(INK, 1.2), QColor('#ffffff'))

    # 中心线：轴向 + 每个孔纵向
    cpen = QPen(CENTER, 1.5, Qt.DashDotLine)
    cpen.setDashPattern([12, 4, 3, 4])
    center = QPainterPath()
    center.moveTo(X(0), Y(0) - 20)
    center.lineTo(X(0), Y(H) + 20)
    for sign in (1, -1):
        hx = X(sign * K / 2)
        center.moveTo(hx, Y(plate_start) - 10)
        center.lineTo(hx, Y(H) + 10)
    spec.path(center, cpen)

    # 尺寸：布局器分道避让
    layout = DimensionLayout(width, height, 13)

    def hdim(r1, r2, y0, text):
        f1 = QPointF(X(r1), Y(H))
        f2 = QPointF(X(r2), Y(H))
        y, pos = layout.place_horizontal(f1.x(), f2.x(), text, y0)
        spec.dimension(QPointF(f1.x(), y), QPointF(f2.x(), y), text,
                       ext1=(f1.x(), f1.y()), ext2=(f2.x(), f2.y()),
                       text_pos=pos)

    hdim(-plate_r, plate_r, top - 56, 'D=%s' % row.get('D', ''))
    hdim(-K / 2, K / 2, top - 96, 'K=%s' % row.get('K', ''))
    if kind not in ('PL', 'BL'):
        hdim(-hub_r, hub_r, top - 136,
             'N=%s' % (row.get('N_A') or ('%g' % N)))

    # H 左侧
    f1 = QPointF(X(-plate_r), Y(0))
    f2 = QPointF(X(-plate_r), Y(H))
    x, pos = layout.place_vertical(f1.y(), f2.y(), 'H=%s' % (
        row.get('H') or ('%g' % H)), X(-plate_r) - 36, -1)
    spec.dimension(QPointF(x, f1.y()), QPointF(x, f2.y()),
                   'H=%s' % (row.get('H') or ('%g' % H)),
                   ext1=(f1.x(), f1.y()), ext2=(f2.x(), f2.y()),
                   text_pos=pos)
    # C 右侧
    f1 = QPointF(X(plate_r), Y(plate_start))
    f2 = QPointF(X(plate_r), Y(H))
    x, pos = layout.place_vertical(f1.y(), f2.y(), 'C=%s' % row.get('C', ''),
                                   X(plate_r) + 36, 1)
    spec.dimension(QPointF(x, f1.y()), QPointF(x, f2.y()),
                   'C=%s' % row.get('C', ''),
                   ext1=(f1.x(), f1.y()), ext2=(f2.x(), f2.y()),
                   text_pos=pos)

    if bore > 0:
        y = Y(H * 0.5)
        spec.dimension(QPointF(X(-bore_r), y), QPointF(X(bore_r), y),
                       'd=%g' % bore, text_pos=QPointF(cx, y - 18))
    spec.text(24, 62, '数据源：%s' % (standard or '内置数据'), 12,
              QColor('#555555'))
    spec.text(24, 84, '参数化矢量图 · 尺寸单位 mm', 12, QColor('#555555'))
    return spec
