# -*- coding: utf-8 -*-
"""参数化绘图核心：DrawingSpec、尺寸布局与矢量输出。"""

from .layout import DimensionLayout
from .renderer import paint_spec, render_image, render_pixmap, save_pdf, save_svg
from .spec import DimensionSpec, DrawingSpec, PathSpec, TextSpec

__all__ = ['DimensionLayout', 'DimensionSpec', 'DrawingSpec', 'PathSpec',
           'TextSpec', 'paint_spec', 'render_image', 'render_pixmap',
           'save_pdf', 'save_svg']
