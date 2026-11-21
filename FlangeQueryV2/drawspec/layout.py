# -*- coding: utf-8 -*-
"""尺寸线布局：文字/尺寸线碰撞避让。"""

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QFont, QFontMetrics


class DimensionLayout:
    """在给定画布内为尺寸文字寻找不重叠的位置。

    尺寸线本身仍由调用方给出；布局器只负责把尺寸线/文字放到不同“道”上，
    并把已占用的文字矩形记录下来，供后续尺寸避让。
    """

    def __init__(self, width, height, font_size=13):
        self.width = width
        self.height = height
        self.font = QFont('Microsoft YaHei')
        self.font.setPixelSize(font_size)
        self.metrics = QFontMetrics(self.font)
        self.reserved = []

    def _text_rect(self, cx, cy, text):
        w = max(40, self.metrics.horizontalAdvance(text) + 8)
        h = self.metrics.height() + 4
        return QRectF(cx - w / 2, cy - h / 2, w, h), w, h

    def _free(self, rect):
        if rect.left() < 2 or rect.right() > self.width - 2:
            return False
        if rect.top() < 2 or rect.bottom() > self.height - 2:
            return False
        return not any(rect.intersects(other) for other in self.reserved)

    def place_horizontal(self, x1, x2, text, base_y, direction=-1):
        """返回 (尺寸线 y, 文字中心 QPointF)。"""
        mid = (x1 + x2) / 2
        y = base_y
        for _ in range(24):
            rect, _, _ = self._text_rect(mid, y - 18, text)
            if self._free(rect):
                self.reserved.append(rect)
                return y, QPointF(mid, y - 18)
            y += direction * 24
        self.reserved.append(rect)
        return y, QPointF(mid, y - 18)

    def place_vertical(self, y1, y2, text, base_x, direction=1):
        """返回 (尺寸线 x, 文字中心 QPointF)。"""
        mid = (y1 + y2) / 2
        x = base_x
        for _ in range(24):
            rect, _, _ = self._text_rect(x, mid, text)
            if self._free(rect):
                self.reserved.append(rect)
                return x, QPointF(x, mid)
            x += direction * 28
        self.reserved.append(rect)
        return x, QPointF(x, mid)
