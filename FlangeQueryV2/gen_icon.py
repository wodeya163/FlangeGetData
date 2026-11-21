# -*- coding: utf-8 -*-
"""生成蓝调扁平法兰应用图标 app_icon.ico（多尺寸）+ icon_preview.png
配色对齐 ui_home_v2b.html（UI 规划第二版）：主蓝 #1f4e79 / #2a5f92，浅蓝 #4a90d9
"""
import math
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
S = 512  # 画布

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def hexc(s, alpha=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), alpha)

# ---- 1) 底：圆角方块，垂直渐变 #2a5f92 -> #16405f ----
top, bot = hexc('#2a5f92'), hexc('#16405f')
grad = Image.new('RGB', (1, S))
for y in range(S):
    grad.putpixel((0, y), lerp(top, bot, y / (S - 1)))
grad = grad.resize((S, S))

mask = Image.new('L', (S, S), 0)
ImageDraw.Draw(mask).rounded_rectangle([8, 8, S - 8, S - 8], radius=104, fill=255)

img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
img.paste(grad, (0, 0), mask)
d = ImageDraw.Draw(img)

# 底板内描边（ subtle 高光边）
d.rounded_rectangle([10, 10, S - 10, S - 10], radius=102,
                    outline=(255, 255, 255, 36), width=3)

CX, CY = S // 2, S // 2 + 6

# ---- 2) 法兰盘（同心圆叠加模拟径向光感）----
R_OUT = 178
inner, outer = hexc('#4f9ad8'), hexc('#275d8e')   # 中心亮 -> 边缘深
steps = 48
for i in range(steps):
    t = i / (steps - 1)
    r = R_OUT * (1 - t * 0.62)          # 从外向内
    col = lerp(outer, inner, t)
    d.ellipse([CX - r, CY - r, CX + r, CY + r], fill=col)

# 外缘描边
d.ellipse([CX - R_OUT, CY - R_OUT, CX + R_OUT, CY + R_OUT],
          outline=hexc('#12365a'), width=5)

# ---- 3) 8 个螺栓孔（浅色，带立体暗边）----
R_RING, R_HOLE = 128, 25
for k in range(8):
    a = math.radians(k * 45 - 90)
    hx, hy = CX + R_RING * math.cos(a), CY + R_RING * math.sin(a)
    d.ellipse([hx - R_HOLE - 3, hy - R_HOLE - 3, hx + R_HOLE + 3, hy + R_HOLE + 3],
              fill=hexc('#1b4a73'))                      # 孔座暗边
    d.ellipse([hx - R_HOLE, hy - R_HOLE, hx + R_HOLE, hy + R_HOLE],
              fill=hexc('#e9f1fa'))                      # 孔
    d.ellipse([hx - R_HOLE + 5, hy - R_HOLE + 5, hx + R_HOLE - 2, hy + R_HOLE - 2],
              outline=hexc('#a9c4de'), width=3)          # 孔内壁

# ---- 4) 中心通径（管道口）----
R_BORE = 82
d.ellipse([CX - R_BORE - 6, CY - R_BORE - 6, CX + R_BORE + 6, CY + R_BORE + 6],
          fill=hexc('#6fa8dc'))                          # 口缘亮环
d.ellipse([CX - R_BORE, CY - R_BORE, CX + R_BORE, CY + R_BORE],
          fill=hexc('#0f2d49'))                          # 通径深孔
# 孔内下缘反光
d.arc([CX - R_BORE + 14, CY - R_BORE + 14, CX + R_BORE - 14, CY + R_BORE - 14],
      start=30, end=150, fill=hexc('#3a6d9e'), width=6)

# ---- 5) （径向渐变已提供质感，不再叠加高光弧）----

# ---- 输出 ----
ico_path = os.path.join(HERE, 'app_icon.ico')
img.save(ico_path, sizes=[(16, 16), (24, 24), (32, 32), (48, 48),
                          (64, 64), (128, 128), (256, 256)])
img.save(os.path.join(HERE, 'icon_preview.png'))
print('OK ->', ico_path)
print('OK ->', os.path.join(HERE, 'icon_preview.png'))
