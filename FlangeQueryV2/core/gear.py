# -*- coding: utf-8 -*-
"""圆柱齿轮几何参数（直齿/斜齿）。"""

import math


def gear_pair(m, z1, z2, alpha=20.0, beta=0.0, x1=0.0, x2=0.0):
    if m <= 0 or z1 < 3 or z2 < 3:
        raise ValueError('模数和齿数必须有效')
    alpha = math.radians(alpha)
    beta = math.radians(beta)
    mt = m / math.cos(beta)
    d1 = mt * z1
    d2 = mt * z2
    alpha_t = math.atan(math.tan(alpha) / math.cos(beta))
    db1 = d1 * math.cos(alpha_t)
    db2 = d2 * math.cos(alpha_t)
    ha = m
    hf = 1.25 * m
    da1 = d1 + 2 * ha + 2 * x1 * m
    da2 = d2 + 2 * ha + 2 * x2 * m
    df1 = d1 - 2 * hf + 2 * x1 * m
    df2 = d2 - 2 * hf + 2 * x2 * m
    a = (d1 + d2) / 2 + (x1 + x2) * m
    ratio = z2 / z1
    s1 = math.pi * m / 2 + 2 * x1 * m * math.tan(alpha)
    s2 = math.pi * m / 2 + 2 * x2 * m * math.tan(alpha)
    return {
        'm': m, 'mt': mt, 'z1': z1, 'z2': z2,
        'alpha': math.degrees(alpha), 'beta': math.degrees(beta),
        'alpha_t': math.degrees(alpha_t),
        'd1': d1, 'd2': d2, 'da1': da1, 'da2': da2,
        'df1': df1, 'df2': df2, 'db1': db1, 'db2': db2,
        'a': a, 'ratio': ratio, 's1': s1, 's2': s2,
        'ha': ha, 'hf': hf,
    }


def contact_ratio(res):
    """端面重合度近似（直齿，标准齿顶）。"""
    a = math.radians(res['alpha'])
    ra1 = res['da1'] / 2
    ra2 = res['da2'] / 2
    rb1 = res['db1'] / 2
    rb2 = res['db2'] / 2
    a12 = res['a']
    if ra1 <= rb1 or ra2 <= rb2:
        return 0.0
    g1 = math.sqrt(ra1 ** 2 - rb1 ** 2)
    g2 = math.sqrt(ra2 ** 2 - rb2 ** 2)
    pb = math.pi * res['m'] * math.cos(a)
    return max(0.0, (g1 + g2 - a12 * math.sin(a)) / pb)


MODULE_FIRST = [1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16, 20,
                25, 32, 40, 50]
MODULE_SECOND = [1.125, 1.375, 1.75, 2.25, 2.75, 3.5, 4.5, 5.5,
                 6.5, 7, 9, 11, 14, 18, 22, 28, 36, 45]


def nearest_module(m):
    """返回最接近的标准模数，优先第一系列。"""
    if m <= 0:
        return None
    first = min(MODULE_FIRST, key=lambda x: abs(x - m))
    second = min(MODULE_SECOND, key=lambda x: abs(x - m))
    if abs(first - m) <= abs(second - m):
        return first
    return second


def spur_gear(m, z, alpha=20.0, ha_star=1.0, c_star=0.25, x=0.0):
    if m <= 0 or z < 1:
        raise ValueError('模数和齿数必须有效')
    a = math.radians(alpha)
    d = m * z
    da = m * (z + 2 * ha_star + 2 * x)
    df = m * ((z - 2 * ha_star - 2 * c_star) + 2 * x)
    db = d * math.cos(a)
    p = math.pi * m
    s = (math.pi / 2 + 2 * x * math.tan(a)) * m
    ha = (ha_star + x) * m
    hf = (ha_star + c_star - x) * m
    return {'d': d, 'da': da, 'df': df, 'db': db, 'p': p, 's': s,
            'ha': ha, 'hf': hf, 'h': ha + hf,
            'sb': db * (s / d + math.tan(a) - a)}


def helical_gear(mn, z, beta, alpha_n=20.0, ha_star=1.0, c_star=0.25,
                 xn=0.0):
    if mn <= 0 or z < 1 or abs(beta) >= 90:
        raise ValueError('模数、齿数或螺旋角无效')
    b = math.radians(beta)
    an = math.radians(alpha_n)
    mt = mn / math.cos(b)
    at = math.atan(math.tan(an) / math.cos(b))
    d = mt * z
    da = d + 2 * (ha_star + xn) * mn
    df = d - 2 * (ha_star + c_star - xn) * mn
    db = d * math.cos(at)
    p = math.pi * mt
    s = (math.pi / 2 + 2 * xn * math.tan(an)) * mn
    ha = ha_star * mn
    hf = (ha_star + c_star) * mn
    return {'mt': mt, 'alpha_t': math.degrees(at), 'd': d, 'da': da,
            'df': df, 'db': db, 'p': p, 's': s,
            'zv': z / math.cos(b) ** 3, 'ha': ha, 'hf': hf,
            'h': ha + hf}


def bevel_gear(z1, z2, m, b, alpha=20.0, ha_star=1.0, c_star=0.25,
               sigma=90.0):
    if z1 < 1 or z2 < 1 or m <= 0 or b <= 0 or not 0 < sigma < 180:
        raise ValueError('锥齿轮参数无效')
    sg = math.radians(sigma)
    delta1 = math.atan2(z1 * math.sin(sg), z2 + z1 * math.cos(sg))
    delta2 = sg - delta1
    d1, d2 = m * z1, m * z2
    R = d1 / (2 * math.sin(delta1))
    if b > R:
        raise ValueError('齿宽超过外锥距')
    ha = ha_star * m
    hf = (ha_star + c_star) * m
    rm = R - b / 2
    return {'delta1': math.degrees(delta1),
            'delta2': math.degrees(delta2), 'R': R,
            'd1': d1, 'd2': d2, 'ha': ha, 'hf': hf, 'h': ha + hf,
            'rm': rm, 'dm1': 2 * rm * math.sin(delta1),
            'dm2': 2 * rm * math.sin(delta2), 'ratio': z2 / z1}


def pair_center_distance(kind, m, z1, z2, beta=0.0, x1=0.0, x2=0.0):
    if m <= 0 or z1 < 1 or z2 < 1:
        raise ValueError('中心距参数无效')
    if kind == 'helical':
        b = math.radians(beta)
        a = m * (z1 + z2) / (2 * math.cos(b))
        ap = a + (x1 + x2) * m / math.cos(b)
    else:
        a = m * (z1 + z2) / 2
        ap = a + (x1 + x2) * m
    return a, ap, z2 / z1
