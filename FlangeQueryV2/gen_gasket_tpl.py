# -*- coding: utf-8 -*-
"""生成垫片示意图（BMP）：与法兰模板风格一致——黑线白底示意图，数值由程序叠加。
输出 6 类垫片断面/型式图到 templates/：
  gasket_flat.bmp        非金属平垫（20606/20627）俯视环
  gasket_spiral.bmp      缠绕式垫片（20610/20631）
  gasket_serrated.bmp    齿形组合垫（20611）啮合断面
  gasket_ring.bmp        金属环垫（20612）八角断面
  gasket_ptfe.bmp        PTFE 包覆垫（20607）
  gasket_metaljacket.bmp 金属包覆垫（20609）
"""
import math
import os

from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
W, H = 596, 498
CX, CY = 298, 300
BLACK = (17, 17, 17)
GREY = (120, 120, 120)


def new_canvas():
    return Image.new('RGB', (W, H), (255, 255, 255))


def save(img, name):
    path = os.path.join(OUT, name)
    img.save(path)
    print('wrote', path)


def ring_outline(d, r2, r1, width=3):
    d.ellipse([CX - r2, CY - r2, CX + r2, CY + r2], outline=BLACK, width=width)
    d.ellipse([CX - r1, CY - r1, CX + r1, CY + r1], outline=BLACK, width=width)


def dashed_circle(d, r, width=2, seg=10):
    step = math.pi / seg
    for i in range(seg * 2):
        a0 = i * step
        a1 = a0 + step * 0.55
        x0, y0 = CX + r * math.cos(a0), CY + r * math.sin(a0)
        x1, y1 = CX + r * math.cos(a1), CY + r * math.sin(a1)
        d.line([x0, y0, x1, y1], fill=GREY, width=width)


def spokes(d, r, n=12):
    for i in range(n):
        a = i * 2 * math.pi / n
        d.line([CX, CY, CX + r * math.cos(a), CY + r * math.sin(a)],
               fill=GREY, width=1)


# ---------------------------------------------------------------- 非金属平垫
def draw_flat():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    ring_outline(d, 165, 100)
    spokes(d, 100, 16)
    save(img, 'gasket_flat.bmp')


# ---------------------------------------------------------------- PTFE 包覆垫
def draw_ptfe():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    ring_outline(d, 165, 100)
    # 包覆层（外缘双线，示意 PTFE 包覆）
    d.ellipse([CX - 156, CY - 156, CX + 156, CY + 156], outline=GREY, width=2)
    d.ellipse([CX - 109, CY - 109, CX + 109, CY + 109], outline=GREY, width=2)
    save(img, 'gasket_ptfe.bmp')


# ---------------------------------------------------------------- 金属包覆垫
def draw_metaljacket():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    ring_outline(d, 165, 100)
    d.ellipse([CX - 158, CY - 158, CX + 158, CY + 158], outline=GREY, width=2)
    spokes(d, 100, 16)
    save(img, 'gasket_metaljacket.bmp')


# ---------------------------------------------------------------- 缠绕式垫片
def draw_spiral():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    ring_outline(d, 165, 100)
    rm = 132
    dashed_circle(d, rm, width=2, seg=14)
    # 缠绕波纹（径向短锯齿，示意金属带缠绕）
    n = 48
    for i in range(n):
        a = i * 2 * math.pi / n
        x0, y0 = CX + 100 * math.cos(a), CY + 100 * math.sin(a)
        x1, y1 = CX + 165 * math.cos(a + 0.04), CY + 165 * math.sin(a + 0.04)
        d.line([x0, y0, x1, y1], fill=GREY, width=2)
    save(img, 'gasket_spiral.bmp')


# ---------------------------------------------------------------- 齿形组合垫（啮合断面）
def draw_serrated():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    x0, x1 = 108, 488
    plate = 16
    ty = 260            # 上板顶
    by = 340            # 下板底
    n = 10
    pitch = (x1 - x0) / n
    # 上板 + 下指（尖朝下）
    d.rectangle([x0, ty, x1, ty + plate], outline=BLACK, width=3)
    # 下板 + 上指（尖朝上）
    d.rectangle([x0, by - plate, x1, by], outline=BLACK, width=3)
    tip = 312
    for i in range(n):
        bx = x0 + i * pitch
        # 上指：从 y=ty+plate 到 tip
        d.polygon([(bx, ty + plate), (bx + pitch, ty + plate),
                   (bx + pitch / 2, tip)], outline=BLACK, width=2)
        # 下指：从 y=by-plate 到 tip（错半齿啮合）
        bx2 = x0 + (i + 0.5) * pitch
        d.polygon([(bx2, by - plate), (bx2 + pitch, by - plate),
                   (bx2 + pitch / 2, tip)], outline=BLACK, width=2)
    save(img, 'gasket_serrated.bmp')


# ---------------------------------------------------------------- 金属环垫（八角断面）
def draw_ring():
    img = new_canvas()
    d = ImageDraw.Draw(img)
    R = 120                       # 外接半径
    verts = []
    for i in range(8):
        a = math.pi / 8 + i * math.pi / 4      # 八角形
        verts.append((CX + R * math.cos(a), CY + R * math.sin(a)))
    d.polygon(verts, outline=BLACK, width=3)
    # 内接参考线（示意节圆 P 与八角平面 B）
    d.ellipse([CX - R + 22, CY - R + 22, CX + R - 22, CY + R - 22],
              outline=GREY, width=1)
    # 中心十字
    d.line([CX - R - 30, CY, CX + R + 30, CY], fill=GREY, width=1)
    d.line([CX, CY - R - 30, CX, CY + R + 30], fill=GREY, width=1)
    save(img, 'gasket_ring.bmp')


if __name__ == '__main__':
    draw_flat()
    draw_ptfe()
    draw_metaljacket()
    draw_spiral()
    draw_serrated()
    draw_ring()
    print('done')
