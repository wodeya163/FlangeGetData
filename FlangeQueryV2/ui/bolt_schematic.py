# -*- coding: utf-8 -*-
"""螺栓群/螺钉连接简图。"""

import math

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QFont, QPainter, QPen, QPolygonF
from PyQt5.QtWidgets import QWidget


class BoltSchematic(QWidget):
    """俯视简图：螺栓均布、横向/轴向力和偏心弯矩方向。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.n = 4
        self.screw = False
        self.fx = 1000.0
        self.fy = 2000.0
        self.moment = 0.0
        self.setMinimumHeight(150)
        self.setMaximumHeight(175)

    def set_data(self, n, screw, fx, fy, moment):
        self.n = max(1, int(n))
        self.screw = bool(screw)
        self.fx = float(fx)
        self.fy = float(fy)
        self.moment = float(moment)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(self.rect(), QColor('#ffffff'))
        p.setPen(QPen(QColor('#c9d2dc'), 1))
        p.drawRoundedRect(1, 1, w - 2, h - 2, 6, 6)
        p.setFont(QFont('Microsoft YaHei', 9))
        p.setPen(QColor('#1f4e79'))
        title = '螺钉连接（螺纹盲孔）' if self.screw else '螺栓群布置（俯视）'
        p.drawText(12, 20, title)
        cx, cy = w * 0.42, h * 0.58
        radius = min(w * 0.22, h * 0.30)
        p.setPen(QPen(QColor('#8a97a8'), 1, Qt.DashLine))
        p.drawEllipse(QPointF(cx, cy), radius, radius)
        if self.screw:
            points = [(cx, cy)]
        elif self.n <= 1:
            points = [(cx, cy)]
        else:
            points = [(cx + radius * math.cos(2 * math.pi * i / self.n),
                       cy - radius * math.sin(2 * math.pi * i / self.n))
                      for i in range(self.n)]
        for i, (x, y) in enumerate(points):
            p.setBrush(QColor('#eef3f8'))
            p.setPen(QPen(QColor('#1f4e79'), 1.4))
            p.drawEllipse(QPointF(x, y), 7, 7)
            p.setPen(QColor('#1f4e79'))
            p.drawText(QPointF(x + 9, y - 5), 'B%d' % (i + 1))
        # 力箭头
        p.setPen(QPen(QColor('#c0392b'), 2))
        self._arrow(p, cx + radius + 10, cy, cx + radius + 48, cy,
                    'Fx %.0f N' % self.fx)
        self._arrow(p, cx, cy - radius - 10, cx, cy - radius - 42,
                    'Fy %.0f N' % self.fy)
        if abs(self.moment) > 1e-9:
            p.setPen(QPen(QColor('#a15c00'), 2))
            p.drawArc(int(cx - radius - 14), int(cy - radius - 14),
                      int(2 * radius + 28), int(2 * radius + 28),
                      30 * 16, 120 * 16)
            p.setPen(QColor('#a15c00'))
            p.drawText(QPointF(cx + radius + 8, cy + radius + 20),
                       'M %.0f N·mm' % self.moment)
        p.setPen(QColor('#667085'))
        p.drawText(12, h - 10,
                   '数量 %d　%s' % (self.n, '螺纹啮合' if self.screw else '摩擦传力'))
        p.end()

    @staticmethod
    def _arrow(p, x1, y1, x2, y2, label):
        p.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        ang = math.atan2(y2 - y1, x2 - x1)
        for da in (2.6, -2.6):
            p.drawLine(QPointF(x2, y2),
                       QPointF(x2 - 9 * math.cos(ang + da),
                               y2 - 9 * math.sin(ang + da)))
        p.drawText(QPointF(x2 - 4, y2 - 8), label)
