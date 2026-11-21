# -*- coding: utf-8 -*-
"""密封面参考图的 DrawingSpec 适配器：RF / MFM / TG / RJ。"""

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QColor, QPainterPath, QPen, QPolygonF

from drawspec.spec import DrawingSpec

INK = QColor('#111111')
FILL = QColor('#eef2f7')
CENTER = QColor('#0b4f8a')
DIM = QColor('#5f6b76')


def build_seal_spec(row, template='mfm_突面.bmp', width=800, height=500):
    name = row.get('名称', '') or row.get('代号', '')
    tpl = template or ''
    if '环连接' in tpl or 'RJ' in name:
        face = 'RJ'
    elif '凹凸' in tpl or 'MFM' in name:
        face = 'MFM'
    elif '楔槽' in tpl or '榫槽' in tpl or 'TG' in name:
        face = 'TG'
    else:
        face = 'RF'
    spec = DrawingSpec(title='密封面 %s %s' % (row.get('代号', ''), name),
                       width=width, height=height,
                       source=row.get('适用标准', ''))
    cx, cy = width / 2, height / 2
    pw, ph, gap = 500, 58, 26
    upper = QRectF(cx - pw / 2, cy - gap / 2 - ph, pw, ph)
    lower = QRectF(cx - pw / 2, cy + gap / 2, pw, ph)
    for rect in (upper, lower):
        p = QPainterPath()
        p.addRect(rect)
        spec.path(p, QPen(INK, 2.0), FILL)
    if face == 'RJ':
        for yy in (upper.bottom() - 6, lower.top() + 6):
            poly = QPolygonF([
                QPointF(cx - 120, yy + 8), QPointF(cx - 80, yy - 14),
                QPointF(cx + 80, yy - 14), QPointF(cx + 120, yy + 8),
                QPointF(cx + 80, yy + 22), QPointF(cx - 80, yy + 22),
            ])
            p = QPainterPath()
            p.addPolygon(poly)
            spec.path(p, QPen(INK, 1.6))
            spec.text(cx - 80, yy - 4, '八角槽', 12, DIM,
                      Qt.AlignHCenter, 160, True)
    elif face == 'MFM':
        p = QPainterPath()
        p.addRect(QRectF(cx - 90, upper.bottom() - 16, 180, 16))
        spec.path(p, QPen(INK, 1.6), QColor('#ffffff'))
        p = QPainterPath()
        p.addRect(QRectF(cx - 80, lower.top() - 14, 160, 14))
        spec.path(p, QPen(INK, 1.6), FILL)
        spec.text(cx - 100, upper.top() + 5, '凹槽', 12, DIM,
                  Qt.AlignHCenter, 200, True)
        spec.text(cx - 100, lower.bottom() - 20, '凸榫', 12, DIM,
                  Qt.AlignHCenter, 200, True)
    elif face == 'TG':
        p = QPainterPath()
        p.addRect(QRectF(cx - 80, upper.bottom() - 14, 160, 14))
        spec.path(p, QPen(INK, 1.6), FILL)
        p = QPainterPath()
        p.addRect(QRectF(cx - 90, lower.top(), 180, 16))
        spec.path(p, QPen(INK, 1.6), QColor('#ffffff'))
        spec.text(cx - 100, upper.top() + 5, '凸榫', 12, DIM,
                  Qt.AlignHCenter, 200, True)
        spec.text(cx - 100, lower.bottom() - 20, '凹槽', 12, DIM,
                  Qt.AlignHCenter, 200, True)
    else:
        p = QPainterPath()
        p.addRect(QRectF(cx - 180, upper.bottom() - 12, 360, 12))
        spec.path(p, QPen(INK, 1.6), FILL)
        spec.text(cx - 100, upper.top() + 5, '突面', 12, DIM,
                  Qt.AlignHCenter, 200, True)
        p = QPainterPath()
        p.moveTo(cx - pw / 2, lower.top())
        p.lineTo(cx + pw / 2, lower.top())
        spec.path(p, QPen(INK, 1.6))

    p = QPainterPath()
    p.moveTo(cx, upper.top() - 20)
    p.lineTo(cx, lower.bottom() + 20)
    pen = QPen(CENTER, 1.5, Qt.DashDotLine)
    pen.setDashPattern([12, 4, 3, 4])
    spec.path(p, pen)
    spec.text(24, 62, '数据源：%s' % row.get('适用标准', ''), 12,
              QColor('#555555'))
    spec.text(24, 84, '沟槽剖面示意 · %s' % row.get('适用压力范围', ''),
              12, QColor('#555555'))
    return spec
