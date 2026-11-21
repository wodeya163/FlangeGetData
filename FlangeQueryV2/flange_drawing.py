# -*- coding: utf-8 -*-
"""GB/T 9124 法兰矢量剖面（横向布置、内孔实线、分道尺寸）。"""

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import (QColor, QPainter, QPainterPath, QPen, QPixmap,
                         QPolygonF)

import bellows_drawing as bd
from bellows_drawing import _arrow, _text

INK = QColor('#111111')
DIM = QColor('#5f6b76')
FILL = QColor('#eef2f7')
BORE = QColor('#111111')
CENTER = QColor('#0b4f8a')

KIND_NAMES = {
    'WN': 'WN 带颈对焊', 'SO': 'SO 带颈平焊', 'PL': 'PL 板式平焊',
    'SW': 'SW 承插焊', 'TH': 'Th 螺纹', 'BL': 'BL 法兰盖',
    'IF': 'IF 整体法兰', 'PJ': 'PJSE/PJRJ 松套',
    'LWN': 'LWN 长高颈',
}


def _f(row, key, default=0.0):
    try:
        return float(str(row.get(key, '')).strip())
    except (TypeError, ValueError):
        return default


def _frame(painter, width, height, row, kind_name='WN 带颈对焊', code='WN',
           standard=''):
    margin = 22
    painter.setPen(QPen(QColor('#333'), 1.5))
    painter.setBrush(Qt.NoBrush)
    painter.drawRect(QRectF(8, 8, width - 16, height - 16))
    painter.setPen(QPen(QColor('#333'), 1))
    painter.drawRect(QRectF(margin, margin, width - 2 * margin,
                            height - 2 * margin))
    bw, bh = 380, 124
    bx, by = width - margin - bw, height - margin - bh
    painter.setBrush(Qt.white)
    painter.setPen(QPen(QColor('#333'), 1.2))
    painter.drawRect(QRectF(bx, by, bw, bh))
    for i in (26, 50, 74, 98):
        painter.drawLine(QPointF(bx, by + i), QPointF(bx + bw, by + i))
    dn = str(row.get('DN', ''))
    std = standard or ('GB/T 9124.1-2019' if row.get('PN')
                       else 'GB/T 9124.2-2019')
    _text(painter, bx + 6, by + 4, '%s钢制管法兰' % kind_name, 11,
          QColor('#222'))
    _text(painter, bx + 230, by + 4, '图号 %s-DN%s' % (code, dn), 10,
          QColor('#222'))
    _text(painter, bx + 6, by + 28, '标准 %s' % std, 10, QColor('#222'))
    _text(painter, bx + 230, by + 28, '规格 DN%s · %s'
          % (dn, ('PN' + row['PN']) if row.get('PN')
             else ('Class ' + row.get('Class', ''))), 10, QColor('#222'))
    _text(painter, bx + 6, by + 52, '型式 %s' % kind_name, 10,
          QColor('#222'))
    _text(painter, bx + 230, by + 52, '材料 待定', 10, QColor('#222'))
    _text(painter, bx + 6, by + 76, '比例 示意（按真实尺寸）', 10,
          QColor('#222'))
    _text(painter, bx + 230, by + 76, '单位 mm', 10, QColor('#222'))
    _text(painter, bx + 6, by + 100, '设计', 9, QColor('#222'))
    _text(painter, bx + 230, by + 100, '审核  第1页 共1页', 9,
          QColor('#222'))


def _dim_h(painter, y, r1, r2, text, xfunc, size=13, arrow=6):
    p1, p2 = QPointF(xfunc(r1), y), QPointF(xfunc(r2), y)
    painter.setPen(QPen(DIM, 1))
    _arrow(painter, p1, p2, arrow)
    for px in (p1.x(), p2.x()):
        painter.drawLine(QPointF(px, y - 5), QPointF(px, y + 5))
    _text(painter, (p1.x() + p2.x()) / 2 - max(70, size * 4), y - 22,
          text, size, DIM, Qt.AlignHCenter, max(140, size * 8), True)


def _dim_v(painter, x, a1, a2, text, yfunc, size=13, arrow=6):
    p1, p2 = QPointF(x, yfunc(a1)), QPointF(x, yfunc(a2))
    painter.setPen(QPen(DIM, 1))
    _arrow(painter, p1, p2, arrow)
    for py in (p1.y(), p2.y()):
        painter.drawLine(QPointF(x - 5, py), QPointF(x + 5, py))
    _text(painter, x - max(60, size * 3), (p1.y() + p2.y()) / 2 - 10,
          text, size, DIM, Qt.AlignHCenter, max(120, size * 6), True)


def render_gb_flange(row, width=1200, height=900, frame=True, kind='WN',
                     show_labels=True, standard='', compact=False, face='RF'):
    kind = (kind or 'WN').upper()
    bd._SHOW_LABELS = show_labels
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
        dn_num = float(str(row.get('DN', '')).rstrip('aA'))
    except ValueError:
        dn_num = 0.0

    if kind == 'PJ':
        H = _f(row, 'h') or _f(row, 'H_d') or H
        N = _f(row, 'B1_A') or _f(row, 'B1_B') or N
    if kind in ('PL', 'BL'):
        H = C
    if kind == 'BL':
        A1, N, S = dn_num, dn_num, 0.0
    if A1 <= 0:
        A1 = dn_num + 6.0
    if N <= 0:
        N = A1
    if kind in ('IF', 'LWN') and H <= 0:
        H = C + max(4.0, (N - A1) / 2.0)
    if min(D, K, C, H, A1) <= 0:
        return None

    plate_r = D / 2.0
    hub_r = N / 2.0
    pipe_r = A1 / 2.0
    plate_start = 0.0 if kind in ('PL', 'BL') else max(0.0, H - C)
    dbore = _f(row, 'd_bore')
    if kind == 'BL':
        bore = 0.0
    elif dbore > 0:
        bore = dbore
    elif S > 0:
        bore = max(1.0, A1 - 2 * S)
    else:
        bore = max(1.0, dn_num)
    bore_r = bore / 2.0
    if compact:
        width, height = 800, 500

    pixmap = QPixmap(width, height)
    pixmap.fill(Qt.white)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)

    # 横向布置：径向为水平 X，轴向为竖直 Y
    if compact:
        width, height = 800, 500
        label_size, arrow_size = 26, 12
        draw_w, draw_h = width - 170, height - 220
        cx = width / 2.0
        scale = min(draw_w / max(D, 1), draw_h / max(H, 1))
        top = max(175.0, (height - H * scale) / 2.0)
    else:
        label_size, arrow_size = 13, 6
        draw_w = width - 420
        draw_h = height - 330
        scale = min(draw_w / max(D, 1), draw_h / max(H, 1))
        cx = width / 2.0
        top = 230

    def X(r):
        return cx + r * scale

    def Y(a):
        return top + a * scale

    face = (face or 'RF').upper()
    rf_d = _f(row, 'RF_d')
    rf_f = _f(row, 'RF_f1')
    approx = rf_d <= 0 or rf_f <= 0 or face in ('MFM', 'TG', 'RJ')
    if rf_d <= 0:
        rf_d = max(bore + 8.0, D * 0.62)
    if rf_f <= 0:
        rf_f = max(2.0, C * 0.08)
    rf_r = min(plate_r, max(bore_r + 0.5, rf_d / 2.0))
    rf_f = min(rf_f, max(1.0, H * 0.2))

    def face_pts(pr):
        """端面剖面点：突面/榫面凸出，凹面/八角槽内凹。"""
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

    if kind == 'BL':
        top_pts = [(0, 0), (0, plate_r), (H, plate_r), (H, 0)]
    elif kind == 'PL':
        top_pts = [(0, bore_r), (0, plate_r)] + face_pts(plate_r)
    elif kind in ('SO', 'SW', 'TH', 'IF', 'PJ'):
        top_pts = [(0, bore_r), (0, hub_r), (plate_start, hub_r),
                   (plate_start, plate_r)] + face_pts(plate_r)
    else:
        top_pts = [(0, bore_r), (0, pipe_r), (plate_start, hub_r),
                   (plate_start, plate_r)] + face_pts(plate_r)

    path = QPainterPath()
    path.moveTo(QPointF(X(top_pts[0][1]), Y(top_pts[0][0])))
    for a, r in top_pts:
        path.lineTo(QPointF(X(r), Y(a)))
    for a, r in reversed(top_pts):
        path.lineTo(QPointF(X(-r), Y(a)))
    path.closeSubpath()
    painter.setBrush(FILL)
    painter.setPen(QPen(INK, 2.2))
    painter.drawPath(path)

    # 内孔：单独加粗实线
    if bore > 0:
        painter.setPen(QPen(BORE, 2.4))
        painter.drawLine(QPointF(X(bore_r), Y(0)),
                         QPointF(X(bore_r), Y(H)))
        painter.drawLine(QPointF(X(-bore_r), Y(0)),
                         QPointF(X(-bore_r), Y(H)))

    # 金属壁剖面线
    wall = QPainterPath(path)
    if bore > 0:
        hole = QPainterPath()
        hole.addRect(QRectF(X(-bore_r), Y(0), 2 * bore_r * scale, H * scale))
        wall = path.subtracted(hole)
    painter.save()
    painter.setClipPath(wall)
    painter.setPen(QPen(QColor('#b9c5d2'), 1))
    rect = path.boundingRect()
    x = rect.left() - rect.height()
    while x < rect.right() + rect.height():
        painter.drawLine(QPointF(x, rect.bottom()),
                         QPointF(x + rect.height(), rect.top()))
        x += 8
    painter.restore()
    painter.setBrush(Qt.NoBrush)
    painter.setPen(QPen(INK, 2.2))
    painter.drawPath(path)

    # 螺栓孔：法兰盘内竖向长孔，孔底止于轮缘端面
    hole_bottom = H - (rf_f if face in ('RF', 'TG') else 0.0)
    hole_h = max(0.5, hole_bottom - plate_start)
    painter.setBrush(Qt.white)
    painter.setPen(QPen(INK, 1.2))
    for sign in (1, -1):
        x1 = X(sign * (K / 2 + L / 2))
        x2 = X(sign * (K / 2 - L / 2))
        painter.drawRect(QRectF(min(x1, x2), Y(plate_start),
                                abs(x2 - x1), hole_h * scale))

    # 中心线：内孔轴线 + 每个螺栓孔轴线
    center_pen = QPen(CENTER, 1.7, Qt.DashDotLine)
    center_pen.setDashPattern([12, 4, 3, 4])
    painter.setPen(center_pen)
    painter.drawLine(QPointF(X(0), Y(0) - 28), QPointF(X(0), Y(H) + 28))
    for sign in (1, -1):
        hx = X(sign * K / 2)
        painter.drawLine(QPointF(hx, Y(plate_start) - 12),
                         QPointF(hx, Y(H) + 12))

    face_names = {'RF': 'RF 突面', 'FF': 'FF 全平面',
                  'MFM': 'MFM 凹凸面', 'TG': 'TG 榫槽面',
                  'RJ': 'RJ 环连接'}
    _text(painter, X(0) - 90, Y(H) + 10,
          '%s%s' % (face_names.get(face, face),
                    '（近似）' if approx else ''),
          18 if compact else 13, QColor('#2f6f9f'), Qt.AlignHCenter, 220)

    # 尺寸：D/K/N 顶部横排；H/C 两侧竖排
    yd = top - 48
    yd2 = top - 92
    yn = Y(0) - 135
    painter.setPen(QPen(DIM, 1))
    painter.drawLine(QPointF(X(-plate_r), Y(H)), QPointF(X(-plate_r), yd))
    painter.drawLine(QPointF(X(plate_r), Y(H)), QPointF(X(plate_r), yd))
    _dim_h(painter, yd, -plate_r, plate_r, 'D=%s' % row.get('D', ''), X, label_size, arrow_size)

    painter.drawLine(QPointF(X(-K / 2), Y(plate_start)), QPointF(X(-K / 2), yd2))
    painter.drawLine(QPointF(X(K / 2), Y(plate_start)), QPointF(X(K / 2), yd2))
    _dim_h(painter, yd2, -K / 2, K / 2, 'K=%s' % row.get('K', ''), X, label_size, arrow_size)

    if kind not in ('PL', 'BL'):
        painter.drawLine(QPointF(X(-hub_r), Y(plate_start)), QPointF(X(-hub_r), yn))
        painter.drawLine(QPointF(X(hub_r), Y(plate_start)), QPointF(X(hub_r), yn))
        _dim_h(painter, yn, -hub_r, hub_r,
               'N=%s' % (row.get('N_A') or ('%g' % N)), X, label_size, arrow_size)

    xh = max(80, X(-plate_r) - 45)
    painter.drawLine(QPointF(X(-plate_r), Y(0)), QPointF(xh, Y(0)))
    painter.drawLine(QPointF(X(-plate_r), Y(H)), QPointF(xh, Y(H)))
    _dim_v(painter, xh, 0, H, 'H=%s' % (row.get('H') or ('%g' % H)), Y, label_size, arrow_size)

    xc = min(width - 80, X(plate_r) + 45)
    painter.drawLine(QPointF(X(plate_r), Y(plate_start)),
                     QPointF(xc, Y(plate_start)))
    painter.drawLine(QPointF(X(plate_r), Y(H)), QPointF(xc, Y(H)))
    _dim_v(painter, xc, plate_start, H, 'C=%s' % row.get('C', ''), Y, label_size, arrow_size)

    if bore > 0:
        ydb = Y(H * 0.5)
        _dim_h(painter, ydb, -bore_r, bore_r, 'd=%s' % ('%g' % bore), X, label_size, arrow_size)

    # 中心线最后绘制，压住尺寸引线，保证清晰
    painter.setPen(center_pen)
    painter.drawLine(QPointF(X(0), Y(0) - 28), QPointF(X(0), Y(H) + 28))
    for sign in (1, -1):
        hx = X(sign * K / 2)
        painter.drawLine(QPointF(hx, Y(plate_start) - 12),
                         QPointF(hx, Y(H) + 12))
        mid = (Y(plate_start) + Y(H)) / 2
        half = max(8.0, L * scale * 0.7)
        painter.drawLine(QPointF(hx - half, mid), QPointF(hx + half, mid))

    grade = ('PN' + row['PN']) if row.get('PN') else (
        'Class ' + row.get('Class', ''))
    std = standard or ('GB/T 9124.1-2019' if row.get('PN')
                       else 'GB/T 9124.2-2019')
    if not compact:
        _text(painter, 30, 18, '%s  %s  DN%s  %s'
          % (std, grade, row.get('DN', ''), KIND_NAMES.get(kind, kind)),
              19, INK, Qt.AlignLeft, 1000)
    parts = ['A 系列']
    if row.get('A1_A'):
        parts.append('A1=%s' % row['A1_A'])
    if row.get('S_min') or row.get('S'):
        parts.append('δ=%s' % (row.get('S_min') or row.get('S')))
    if row.get('H1_mean'):
        parts.append('H1=%s' % row['H1_mean'])
    if row.get('R'):
        parts.append('R=%s' % row['R'])
    if bore > 0:
        parts.append('内径 d=%g' % bore)
    parts.append('螺栓 %d-φ%s %s' % (n, row.get('L', ''), row.get('Th', '')))
    if not compact:
        _text(painter, 30, 48, '  '.join(parts), 13, QColor('#333'),
              Qt.AlignLeft, 1100)

    if frame and not compact:
        _frame(painter, width, height, row, KIND_NAMES.get(kind, kind), kind,
               standard)
    painter.end()
    bd._SHOW_LABELS = True
    return pixmap


def compact_labels(row, kind='WN'):
    grade = ('PN' + row.get('PN', '')) if row.get('PN') else (
        'Class ' + row.get('Class', ''))
    return {
        'dn': ((30, 12, 500, 32), 'DN {DN}'),
        'type': ((30, 48, 900, 26), '%s  %s'
                 % (KIND_NAMES.get(kind, kind), grade)),
    }
