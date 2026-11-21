# -*- coding: utf-8 -*-
"""生成管件示意图（BMP）：弯头 / 三通 / 异径管 / 管帽，并叠加尺寸标注。
图形风格与法兰模板一致：黑线白底、带尺寸线与箭头、标注位留白。
"""
import os

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QColor, QFont, QImage, QPainter, QPen, QPolygonF
from PyQt5.QtWidgets import QApplication

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
W, H = 520, 460

LINE = QColor('#111')
DIM = QColor('#444')
FILL = QColor('#f2f4f7')


def arrow(p, ang, painter):
    """尺寸线箭头。"""
    import math
    a1 = ang + math.radians(155)
    a2 = ang - math.radians(155)
    L = 9
    pts = [p,
           QPointF(p.x() + L * math.cos(a1), p.y() + L * math.sin(a1)),
           QPointF(p.x() + L * math.cos(a2), p.y() + L * math.sin(a2))]
    painter.setBrush(LINE)
    painter.drawPolygon(QPolygonF(pts))
    painter.setBrush(Qt.NoBrush)


def dim_h(painter, x1, x2, y, txt, above=True, ext=8):
    """水平尺寸线。"""
    painter.setPen(QPen(DIM, 1))
    painter.drawLine(QPointF(x1, y), QPointF(x2, y))
    arrow(QPointF(x1, y), 3.1416, painter)
    arrow(QPointF(x2, y), 0, painter)


def dim_v(painter, y1, y2, x, txt, left=True):
    """垂直尺寸线。"""
    painter.setPen(QPen(DIM, 1))
    painter.drawLine(QPointF(x, y1), QPointF(x, y2))
    arrow(QPointF(x, y1), -1.5708, painter)
    arrow(QPointF(x, y2), 1.5708, painter)


def base_image():
    img = QImage(W, H, QImage.Format_ARGB32)
    img.fill(Qt.white)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(LINE, 2))
    p.setBrush(FILL)
    return img, p


def finish(img, p, name):
    p.end()
    path = os.path.join(OUT, name)
    img.save(path, 'BMP')
    print('saved', name, img.width(), 'x', img.height())


# ---------------------------------------------------------------- 90° 弯头
def elbow():
    img, p = base_image()
    # 弯头外轮廓：中心线圆角
    R_out, R_in = 150, 88          # 外/内半径（示意）
    cx, cy = 250, 230
    d = 150                        # 两端伸出长度
    # 外弧
    p.drawArc(QRectF(cx - R_out, cy - R_out, R_out * 2, R_out * 2),
              0, 90 * 16)
    # 内弧
    p.drawArc(QRectF(cx - R_in, cy - R_in, R_in * 2, R_in * 2),
              0, 90 * 16)
    # 两端封口（斜口）
    p.drawLine(QPointF(cx + R_in, cy), QPointF(cx + R_out, cy))
    p.drawLine(QPointF(cx, cy - R_in), QPointF(cx, cy - R_out))
    # 中心线
    p.setPen(QPen(QColor('#888'), 1, Qt.DashLine))
    p.drawArc(QRectF(cx - (R_out + R_in) / 2 - 6, cy - (R_out + R_in) / 2 - 6,
                     (R_out + R_in) + 12, (R_out + R_in) + 12), 0, 90 * 16)
    p.drawLine(QPointF(cx + R_in - 20, cy + 24), QPointF(cx + R_out + 24, cy + 24))
    p.drawLine(QPointF(cx - 24, cy - R_in + 24), QPointF(cx - 24, cy - R_out - 16))

    # 尺寸：中心至端面 F
    p.setPen(QPen(DIM, 1))
    px = cx + R_out + 46
    p.drawLine(QPointF(cx, cy), QPointF(px + 6, cy))
    p.drawLine(QPointF(cx, cy), QPointF(cx, cy - R_out - 46))
    dim_v(p, cy - R_out, cy, -0, '')  # 占位不用
    # F：从圆心到右端面（水平）
    dim_h(p, cx, cx + R_out, cy + 62, 'F')
    dim_v(p, cy - R_out, cy, cx - 62, 'F', left=True)
    # D 外径
    dim_v(p, cy - R_out, cy, cx + 92, 'D', left=False)
    finish(img, p, 'fittings_elbow.bmp')


# ---------------------------------------------------------------- 三通
def tee():
    img, p = base_image()
    cx, cy = 260, 300
    w2, t = 66, 110        # 主管半宽 / 支管长度
    body = QRectF(cx - 170, cy - w2, 340, w2 * 2)
    p.drawRect(body)
    br = QRectF(cx - w2, cy - w2 - t, w2 * 2, t)
    p.drawRect(br)
    # 内部相交线去掉效果：重描轮廓
    p.setBrush(Qt.NoBrush)
    p.setPen(QPen(LINE, 2))
    pts = [QPointF(cx - 170, cy - w2), QPointF(cx - w2, cy - w2),
           QPointF(cx - w2, cy - w2 - t), QPointF(cx + w2, cy - w2 - t),
           QPointF(cx + w2, cy - w2), QPointF(cx + 170, cy - w2),
           QPointF(cx + 170, cy + w2), QPointF(cx - 170, cy + w2),
           QPointF(cx - 170, cy - w2)]
    p.drawPolyline(QPolygonF(pts))
    # 中心线
    p.setPen(QPen(QColor('#888'), 1, Qt.DashLine))
    p.drawLine(QPointF(cx - 190, cy), QPointF(cx + 190, cy))
    p.drawLine(QPointF(cx, cy - w2 - t - 30), QPointF(cx, cy + w2 + 30))
    # C 中心至端面
    dim_h(p, cx, cx + 170, cy + w2 + 40, 'C', above=False)
    dim_v(p, cy - w2 - t, cy, cx - 200, 'C', left=True)
    # D
    dim_v(p, cy - w2, cy + w2, cx + 196, 'D', left=False)
    finish(img, p, 'fittings_tee.bmp')


# ---------------------------------------------------------------- 异径管
def reducer():
    img, p = base_image()
    cy = 250
    x1, x2 = 110, 420
    r1, r2 = 130, 78
    p.setBrush(FILL)
    pts = [QPointF(x1, cy - r1), QPointF(x2, cy - r2),
           QPointF(x2, cy + r2), QPointF(x1, cy + r1), QPointF(x1, cy - r1)]
    p.drawPolygon(QPolygonF(pts))
    p.setPen(QPen(QColor('#888'), 1, Qt.DashLine))
    p.drawLine(QPointF(x1 - 34, cy), QPointF(x2 + 34, cy))
    # H 端面至端面
    dim_h(p, x1, x2, cy + r1 + 42, 'H', above=False)
    # 大端 D
    dim_v(p, cy - r1, cy + r1, x1 - 34, 'D', left=True)
    # 小端 D1
    dim_v(p, cy - r2, cy + r2, x2 + 34, 'D1', left=False)
    finish(img, p, 'fittings_reducer.bmp')


# ---------------------------------------------------------------- 管帽
def cap():
    img, p = base_image()
    cy = 250
    x1 = 110
    L, r = 250, 92
    # 椭圆封头轮廓：直段 + 半椭圆
    pts = [QPointF(x1, cy - r)]
    pts.append(QPointF(x1 + L * 0.42, cy - r))
    # 半椭圆
    import math
    for i in range(1, 25):
        th = math.pi / 2 * i / 24
        pts.append(QPointF(x1 + L * 0.42 + L * 0.58 * math.sin(th),
                           cy - r * math.cos(th)))
    for i in range(1, 25):
        th = math.pi / 2 * (1 - i / 24)
        pts.append(QPointF(x1 + L * 0.42 + L * 0.58 * math.sin(th),
                           cy + r * math.cos(th)))
    pts.append(QPointF(x1, cy + r))
    p.drawPolygon(QPolygonF(pts))
    p.setPen(QPen(QColor('#888'), 1, Qt.DashLine))
    p.drawLine(QPointF(x1 - 30, cy), QPointF(x1 + L + 24, cy))
    # E 长度
    dim_h(p, x1, x1 + L, cy + r + 44, 'E', above=False)
    # D 外径
    dim_v(p, cy - r, cy + r, x1 - 30, 'D', left=True)
    finish(img, p, 'fittings_cap.bmp')


def main():
    app = QApplication([])  # noqa: F841  QPainter 需要 QGui 环境
    elbow()
    tee()
    reducer()
    cap()


if __name__ == '__main__':
    main()
