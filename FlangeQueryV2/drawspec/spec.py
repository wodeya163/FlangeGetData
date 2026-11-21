# -*- coding: utf-8 -*-
"""与 Qt 无关的绘图描述模型（仅使用 QtGui 的路径与画笔）。"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPainterPath, QPen


@dataclass
class PathSpec:
    path: QPainterPath
    pen: QPen
    brush: QBrush = field(default_factory=lambda: QBrush(Qt.NoBrush))


@dataclass
class TextSpec:
    x: float
    y: float
    text: str
    size: int = 14
    color: QColor = field(default_factory=lambda: QColor('#111111'))
    align: int = Qt.AlignLeft
    width: int = 300
    background: bool = False


@dataclass
class DimensionSpec:
    """一条尺寸线。p1/p2 是尺寸线端点，ext1/ext2 是轮廓引出点。"""

    p1: QPointF
    p2: QPointF
    text: str
    ext1: Optional[Tuple[float, float]] = None
    ext2: Optional[Tuple[float, float]] = None
    text_pos: Optional[QPointF] = None
    size: int = 13


@dataclass
class DrawingSpec:
    title: str
    width: int = 1200
    height: int = 900
    paths: List[PathSpec] = field(default_factory=list)
    dimensions: List[DimensionSpec] = field(default_factory=list)
    texts: List[TextSpec] = field(default_factory=list)
    source: str = ''

    def path(self, path, pen, brush=None):
        self.paths.append(PathSpec(path, pen, brush or QBrush(Qt.NoBrush)))

    def text(self, x, y, text, size=14, color=None, align=Qt.AlignLeft,
             width=300, background=False):
        self.texts.append(TextSpec(
            x, y, text, size, color or QColor('#111111'), align, width,
            background))

    def dimension(self, p1, p2, text, ext1=None, ext2=None, text_pos=None,
                  size=13):
        self.dimensions.append(DimensionSpec(
            p1, p2, text, ext1, ext2, text_pos, size))
