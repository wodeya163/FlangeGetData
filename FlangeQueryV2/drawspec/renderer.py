# -*- coding: utf-8 -*-
"""DrawingSpec 渲染器：屏幕、PDF、SVG 共用同一套矢量绘制。"""

import math

from PyQt5.QtCore import QPointF, QRect, QSize, Qt
from PyQt5.QtGui import (QColor, QFont, QFontMetrics, QImage, QPageSize,
                         QPainter, QPen, QPdfWriter, QPixmap)
from PyQt5.QtSvg import QSvgGenerator

DIM = QColor('#5f6b76')
INK = QColor('#111111')


def _arrow(painter, p1, p2, size=7):
    painter.drawLine(p1, p2)
    for tip, other in ((p1, p2), (p2, p1)):
        angle = math.atan2(other.y() - tip.y(), other.x() - tip.x())
        for sign in (1, -1):
            a = angle + sign * 0.38
            painter.drawLine(tip, QPointF(tip.x() + size * math.cos(a),
                                        tip.y() + size * math.sin(a)))


def paint_spec(painter, spec):
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)
    for p in spec.paths:
        painter.setPen(p.pen)
        painter.setBrush(p.brush)
        painter.drawPath(p.path)

    for dim in spec.dimensions:
        painter.setPen(QPen(DIM, 1))
        if dim.ext1:
            painter.drawLine(QPointF(*dim.ext1), dim.p1)
        if dim.ext2:
            painter.drawLine(QPointF(*dim.ext2), dim.p2)
        _arrow(painter, dim.p1, dim.p2, 7)
        text = dim.text
        pos = dim.text_pos or QPointF((dim.p1.x() + dim.p2.x()) / 2,
                                      (dim.p1.y() + dim.p2.y()) / 2)
        font = QFont('Microsoft YaHei')
        font.setPixelSize(dim.size)
        painter.setFont(font)
        fm = QFontMetrics(font)
        w = max(50, fm.horizontalAdvance(text) + 8)
        h = fm.height() + 4
        rect = QRect(int(pos.x() - w / 2), int(pos.y() - h / 2), int(w), int(h))
        painter.fillRect(rect, QColor('#ffffff'))
        painter.setPen(DIM)
        painter.drawText(rect, Qt.AlignCenter, text)

    for t in spec.texts:
        font = QFont('Microsoft YaHei')
        font.setPixelSize(t.size)
        painter.setFont(font)
        if t.background:
            fm = QFontMetrics(font)
            w = max(40, fm.horizontalAdvance(t.text) + 8)
            h = fm.height() + 4
            painter.fillRect(QRect(int(t.x), int(t.y - h / 2), w, h),
                             QColor('#ffffff'))
        painter.setPen(t.color)
        painter.drawText(QRect(int(t.x), int(t.y - 12), int(t.width), 24),
                         t.align | Qt.AlignVCenter, t.text)

    if spec.title:
        font = QFont('Microsoft YaHei')
        font.setPixelSize(18)
        painter.setFont(font)
        painter.setPen(INK)
        painter.drawText(QRect(24, 12, spec.width - 48, 28),
                         Qt.AlignLeft | Qt.AlignVCenter, spec.title)


def render_pixmap(spec):
    pm = QPixmap(spec.width, spec.height)
    pm.fill(Qt.white)
    p = QPainter(pm)
    paint_spec(p, spec)
    p.end()
    return pm


def render_image(spec):
    pm = render_pixmap(spec)
    return pm.toImage().convertToFormat(QImage.Format_RGB32)


def save_pdf(spec, path, page=QPageSize.A4):
    writer = QPdfWriter(path)
    writer.setPageSize(QPageSize(page))
    writer.setResolution(300)
    writer.setTitle(spec.title or 'drawing')
    p = QPainter(writer)
    try:
        rect = writer.pageLayout().paintRectPixels(writer.resolution())
        scale = min(rect.width() / max(1, spec.width),
                    rect.height() / max(1, spec.height))
        p.translate(rect.left(), rect.top())
        p.scale(scale, scale)
        paint_spec(p, spec)
    finally:
        p.end()


def save_svg(spec, path):
    gen = QSvgGenerator()
    gen.setFileName(path)
    gen.setSize(QSize(spec.width, spec.height))
    gen.setViewBox(QRect(0, 0, spec.width, spec.height))
    gen.setTitle(spec.title or 'drawing')
    gen.setDescription(spec.source)
    p = QPainter(gen)
    try:
        paint_spec(p, spec)
    finally:
        p.end()
