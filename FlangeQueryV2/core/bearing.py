# -*- coding: utf-8 -*-
"""深沟球轴承选型：当量动载荷、L10h 寿命、静安全系数。"""

from core.bearing_data_table import DEEP_GROOVE

XY = [
    (0.014, 0.19, 2.3), (0.028, 0.22, 1.99), (0.056, 0.26, 1.71),
    (0.084, 0.28, 1.55), (0.11, 0.30, 1.45), (0.17, 0.34, 1.31),
    (0.28, 0.38, 1.15), (0.42, 0.42, 1.04), (0.56, 0.44, 1.00),
]


def xy_factors(fa_over_c0):
    if fa_over_c0 <= XY[0][0]:
        return XY[0][1], XY[0][2]
    for i in range(len(XY) - 1):
        t0, e0, y0 = XY[i]
        t1, e1, y1 = XY[i + 1]
        if fa_over_c0 <= t1:
            f = (fa_over_c0 - t0) / (t1 - t0)
            return e0 + f * (e1 - e0), y0 + f * (y1 - y0)
    return XY[-1][1], XY[-1][2]


def equivalent_load(spec, fr, fa):
    """spec=(d,D,B,Cr,C0r,n_grease,n_oil)，载荷 kN。"""
    e, y = xy_factors(fa / spec[4] if spec[4] else 0)
    if fr <= 0 and fa <= 0:
        return 0.0, e, y
    if fa <= 0 or fa / fr <= e:
        p = fr
    else:
        p = 0.56 * fr + y * fa
    return max(p, fr), e, y


def static_safety(spec, fr, fa):
    p0 = max(0.6 * fr + 0.5 * fa, fr)
    if p0 <= 0:
        return 0.0, float('inf')
    return p0, spec[4] / p0


def life_hours(spec, p, rpm, lubricant='grease', seal_factor=1.0):
    n_limit = spec[5] if lubricant == 'grease' else spec[6] * seal_factor
    over = rpm > n_limit
    if p <= 0 or rpm <= 0:
        return float('inf'), over
    l10_rev = (spec[3] / p) ** 3 * 1e6
    return l10_rev / (60.0 * rpm), over


def recommend(fr, fa, rpm, target_h, lubricant='grease', bore=None):
    hits = []
    for code, spec in sorted(DEEP_GROOVE.items(),
                             key=lambda kv: (kv[1][1], kv[1][0])):
        if bore is not None and spec[0] != bore:
            continue
        p, e, y = equivalent_load(spec, fr, fa)
        l10, over = life_hours(spec, p, rpm, lubricant)
        if over or l10 < target_h:
            continue
        hits.append({
            'code': code, 'd': spec[0], 'D': spec[1], 'B': spec[2],
            'Cr': spec[3], 'C0r': spec[4], 'P': round(p, 2),
            'L10h': round(l10), 'e': e, 'y': y,
        })
    return hits


def check(code, fr, fa, rpm, target_h, lubricant='grease'):
    spec = DEEP_GROOVE.get(code)
    if spec is None:
        raise ValueError('未知轴承型号：%s' % code)
    p, e, y = equivalent_load(spec, fr, fa)
    l10, over = life_hours(spec, p, rpm, lubricant)
    p0, s0 = static_safety(spec, fr, fa)
    return {
        'code': code, 'd': spec[0], 'D': spec[1], 'B': spec[2],
        'Cr': spec[3], 'C0r': spec[4], 'P': p, 'e': e, 'y': y,
        'L10h': l10, 'over_speed': over,
        'P0': p0, 'S0': s0,
        'pass': (l10 >= target_h) and not over and s0 >= 1.0,
    }
