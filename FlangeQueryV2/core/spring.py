# -*- coding: utf-8 -*-
"""圆柱压缩弹簧计算。"""

import math


def compression_spring(d, D, n, G=79000.0, F=100.0, clearance=1.0):
    if d <= 0 or D <= 0 or n <= 0 or G <= 0 or F <= 0:
        raise ValueError('弹簧参数必须大于 0')
    if D <= d:
        raise ValueError('弹簧中径必须大于线径')
    C = D / d
    if C < 4:
        raise ValueError('旋绕比 D/d 建议不小于 4')
    Kw = (4 * C - 1) / (4 * C - 4) + 0.615 / C
    rate = G * d ** 4 / (8 * D ** 3 * n)  # N/mm
    deflection = F / rate
    stress = Kw * 8 * F * D / (math.pi * d ** 3)
    solid = n * d
    free = solid + deflection + clearance
    return {
        'd': d, 'D': D, 'n': n, 'G': G, 'F': F, 'C': C, 'Kw': Kw,
        'rate': rate, 'deflection': deflection, 'stress': stress,
        'solid': solid, 'free': free,
    }
