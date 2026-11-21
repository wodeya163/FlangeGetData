# -*- coding: utf-8 -*-
"""平键选型与强度校核（GB/T 1096 / GB/T 1095）。

数据表取自反编译的 key_data.py；这里重写为可验证的纯函数。
"""

from .key_tolerance import fit_rows, tolerance_rows

PARALLEL_KEY_TABLE = [
    (6, 8, 2, 2), (8, 10, 3, 3), (10, 12, 4, 4),
    (12, 17, 5, 5), (17, 22, 6, 6), (22, 30, 8, 7),
    (30, 38, 10, 8), (38, 44, 12, 8), (44, 50, 14, 9),
    (50, 58, 16, 10), (58, 65, 18, 11), (65, 75, 20, 12),
    (75, 85, 22, 14), (85, 95, 25, 14), (95, 110, 28, 16),
    (110, 130, 32, 18), (130, 150, 36, 20), (150, 170, 40, 22),
    (170, 200, 45, 25), (200, 230, 50, 28), (230, 260, 56, 32),
    (260, 290, 63, 32), (290, 330, 70, 36), (330, 380, 80, 40),
    (380, 440, 90, 45), (440, 500, 100, 50),
]

KEYWAY_DEPTH_TABLE = [
    (6, 8, 1.2, 1.0), (8, 10, 1.8, 1.4), (10, 12, 2.5, 1.8),
    (12, 17, 3.0, 2.3), (17, 22, 3.5, 2.8), (22, 30, 4.0, 3.3),
    (30, 38, 5.0, 3.3), (38, 44, 5.0, 3.3), (44, 50, 5.5, 3.8),
    (50, 58, 6.0, 4.3), (58, 65, 7.0, 4.4), (65, 75, 7.5, 4.9),
    (75, 85, 9.0, 5.4), (85, 95, 9.0, 5.4), (95, 110, 10.0, 6.4),
    (110, 130, 11.0, 7.4), (130, 150, 12.0, 8.4),
    (150, 170, 13.0, 9.4), (170, 200, 15.0, 10.4),
    (200, 230, 17.0, 11.4), (230, 260, 20.0, 12.4),
    (260, 290, 20.0, 12.4), (290, 330, 22.0, 14.4),
    (330, 380, 25.0, 15.4), (380, 440, 28.0, 17.4),
    (440, 500, 31.0, 19.4),
]

KEY_LENGTH_SERIES = [
    6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40, 45,
    50, 56, 63, 70, 80, 90, 100, 110, 125, 140, 160, 180, 200,
    220, 250, 280, 320, 360, 400, 450, 500,
]

ALLOWABLE_STRESS = {
    '钢': {'静载荷': 125, '轻微冲击': 100, '冲击': 60},
    '铸铁': {'静载荷': 70, '轻微冲击': 50, '冲击': 30},
}


def _row(table, d):
    if d <= 0:
        raise ValueError('轴径必须大于 0')
    for lo, hi, a, b in table:
        if lo < d <= hi:
            return a, b
    if d <= table[0][0]:
        return table[0][2], table[0][3]
    return table[-1][2], table[-1][3]


def parallel_key(d):
    b, h = _row(PARALLEL_KEY_TABLE, d)
    return {'b': b, 'h': h}


def keyway_depth(d):
    t1, t2 = _row(KEYWAY_DEPTH_TABLE, d)
    return {'t1': t1, 't2': t2}


def select_length(b, hub_width):
    if hub_width <= 0:
        raise ValueError('轮毂宽度必须大于 0')
    if hub_width < b:
        raise ValueError('轮毂宽度小于键宽')
    candidates = [x for x in KEY_LENGTH_SERIES
                  if b <= x <= max(b, hub_width - 3)]
    if not candidates:
        candidates = [x for x in KEY_LENGTH_SERIES if x >= b]
    if not candidates:
        raise ValueError('轮毂宽度过小')
    return max(candidates)


def check(d, torque_nm, hub_width, hub_material='钢',
          load_type='静载荷', key_material='45钢'):
    """平键选型 + 挤压/剪切校核。torque_nm: N·m。"""
    if torque_nm <= 0:
        raise ValueError('扭矩必须大于 0')
    if hub_material not in ALLOWABLE_STRESS:
        raise ValueError('未知轮毂材料：%s' % hub_material)
    if load_type not in ALLOWABLE_STRESS[hub_material]:
        raise ValueError('未知载荷性质：%s' % load_type)
    dims = parallel_key(d)
    depth = keyway_depth(d)
    b, h = dims['b'], dims['h']
    length = select_length(b, hub_width)
    work = length - b
    if work <= 0:
        work = length
    torque = torque_nm * 1000.0
    sigma = 2 * torque / (d * (h / 2.0) * work)
    tau = 2 * torque / (d * b * work)
    allowable_p = ALLOWABLE_STRESS[hub_material][load_type]
    allowable_tau = KEY_MATERIALS.get(key_material, 60)
    ratio_p = sigma / allowable_p * 100
    ratio_t = tau / allowable_tau * 100
    ratio = max(ratio_p, ratio_t)
    return {
        'd': d, 'b': b, 'h': h, 'L': length, 'hub_width': hub_width,
        'tolerances': tolerance_rows(b, h, length, 'N9', 'JS9'),
        'tol': dict(KEY_TOL),
        't1': depth['t1'], 't2': depth['t2'],
        'work': work, 'torque': torque,
        'sigma_p': sigma, 'allowable_p': allowable_p,
        'tau': tau, 'allowable_tau': allowable_tau,
        'key_material': key_material,
        'ratio_p': ratio_p, 'ratio_t': ratio_t, 'ratio': ratio,
        'safe': ratio <= 100.0,
        'safety_factor': (100.0 / ratio) if ratio > 0 else 999.0,
        'hub_material': hub_material, 'load_type': load_type,
    }


def auto_length(b):
    """按约 3.3b 估算键长，并取标准系列。"""
    target = 3.3 * b
    for value in KEY_LENGTH_SERIES:
        if value >= target:
            return value
    return KEY_LENGTH_SERIES[-1]


def smart(d, torque_nm, hub_width=32.0, hub_material='钢',
          load_type='静载荷'):
    """智能选型：截面/键槽/键长/强度/配合一次给出。"""
    dims = parallel_key(d)
    depth = keyway_depth(d)
    b, h = dims['b'], dims['h']
    hub_auto = hub_width is None
    if hub_auto:
        hub_width = 4.0 * b
    length = auto_length(b)
    if hub_width and hub_width > b + 5:
        candidates = [x for x in KEY_LENGTH_SERIES
                      if b <= x <= hub_width - 5]
        if candidates:
            length = max(candidates)
    work = max(1.0, length - b)
    torque = torque_nm * 1000.0
    sigma = 2 * torque / (d * (h / 2.0) * work)
    allowable = ALLOWABLE_STRESS[hub_material][load_type]
    ratio = sigma / allowable * 100
    return {
        'd': d, 'b': b, 'h': h, 'L': length, 'hub_width': hub_width,
        'hub_auto': hub_auto,
        't1': depth['t1'], 't2': depth['t2'], 'work': work,
        'sigma_p': sigma, 'allowable_p': allowable, 'ratio': ratio,
        'safe': ratio <= 100.0,
        'fit_key': KEY_TOL['b'], 'fit_shaft': 'N9', 'fit_hub': 'JS9',
        'tolerances': tolerance_rows(b, h, length, 'N9', 'JS9'),
        'tol': dict(KEY_TOL),
        'fit_name': '正常联结',
        'mark': '键B %d×%d×%d GB/T 1096-2003' % (b, h, length),
        'hub_material': hub_material, 'load_type': load_type,
        'standard': 'GB/T 1096-2003',
    }


WOODRUFF_KEY_TABLE = [
    ('1×1.4×4', 1, 1.4, 4, 3, 4), ('1.5×2.6×7', 1.5, 2.6, 7, 4, 5),
    ('2×2.6×7', 2, 2.6, 7, 5, 6), ('2×3.7×10', 2, 3.7, 10, 6, 7),
    ('2.5×3.7×10', 2.5, 3.7, 10, 7, 8), ('3×5×13', 3, 5, 13, 8, 10),
    ('3×6.5×16', 3, 6.5, 16, 10, 12), ('4×6.5×16', 4, 6.5, 16, 12, 14),
    ('4×7.5×19', 4, 7.5, 19, 14, 16), ('5×6.5×16', 5, 6.5, 16, 16, 18),
    ('5×7.5×19', 5, 7.5, 19, 18, 20), ('5×9×22', 5, 9, 22, 20, 22),
    ('6×9×22', 6, 9, 22, 22, 25), ('6×10×25', 6, 10, 25, 25, 28),
    ('8×11×28', 8, 11, 28, 28, 32), ('10×13×32', 10, 13, 32, 32, 38),
]

SPLINE_TABLE = [
    ('6×23×26×6', 6, 23, 26, 6), ('6×26×30×6', 6, 26, 30, 6),
    ('6×28×32×7', 6, 28, 32, 7), ('8×32×36×6', 8, 32, 36, 6),
    ('8×36×40×7', 8, 36, 40, 7), ('8×42×46×8', 8, 42, 46, 8),
    ('8×46×50×9', 8, 46, 50, 9), ('8×52×58×10', 8, 52, 58, 10),
    ('8×56×62×10', 8, 56, 62, 10), ('8×62×68×12', 8, 62, 68, 12),
    ('10×72×78×12', 10, 72, 78, 12), ('10×82×88×12', 10, 82, 88, 12),
    ('10×92×98×14', 10, 92, 98, 14), ('10×102×108×16', 10, 102, 108, 16),
    ('10×112×120×18', 10, 112, 120, 18),
]

FITS = [('松联结', 'H9', 'D10'), ('正常联结', 'N9', 'JS9'),
        ('紧密联结', 'P9', 'P9')]
KEY_TOL = {'b': 'h8', 'h': 'h11', 'L': 'h14'}
KEY_MATERIALS = {'45钢': 60, '40Cr': 70, '不锈钢': 50}


def fit_for(load_type='静载荷', need_move=False, precision='一般'):
    if need_move:
        return FITS[0]
    if load_type == '冲击':
        return FITS[2]
    if precision == '高':
        return FITS[1]
    return FITS[1]


def woodruff_key(d):
    for code, b, h, d1, lo, hi in WOODRUFF_KEY_TABLE:
        if lo <= d <= hi:
            return {'code': code, 'b': b, 'h': h, 'd1': d1}
    return None


def woodruff_options(d):
    hits = [item for item in (
        {'code': c, 'b': b, 'h': h, 'd1': d1}
        for c, b, h, d1, lo, hi in WOODRUFF_KEY_TABLE if lo <= d <= hi)]
    if hits:
        return hits
    nearest = sorted(WOODRUFF_KEY_TABLE, key=lambda r: abs(d - (r[4] + r[5]) / 2))[:3]
    return [{'code': c, 'b': b, 'h': h, 'd1': d1}
            for c, b, h, d1, lo, hi in nearest]


def woodruff_check(d, torque_nm, material='钢', load_type='静载荷',
                   code=None):
    item = None
    if code:
        item = next((x for x in woodruff_options(d) if x['code'] == code), None)
    if item is None:
        item = woodruff_key(d)
    if item is None:
        raise ValueError('该轴径无半圆键规格')
    torque = torque_nm * 1000.0
    sigma = 2 * torque / (d * (item['h'] / 2.0) * (item['d1'] / 2.0))
    allowable = ALLOWABLE_STRESS[material][load_type]
    ratio = sigma / allowable * 100
    item.update({'sigma_p': sigma, 'allowable': allowable, 'ratio': ratio,
                 'safe': ratio <= 100.0, 'tol': {'b': 'h9', 'h': 'h11',
                 'd1': 'h12'}, 'fit_shaft': 'N9', 'fit_hub': 'JS9',
                 'tolerances': tolerance_rows(
                     item['b'], item['h'], item['d1'], 'N9', 'JS9',
                     width_grade='h9', height_grade='h11',
                     length_grade='h12', length_label='键径 d1')})
    return item


def taper_check(d, torque_nm, length, material='钢', load_type='静载荷',
                kind='A', hub_width=None):
    b = parallel_key(d)['b']
    if length is None:
        length = taper_length(b, hub_width or 4 * b, kind)
    work = max(1.0, length - b)
    torque = torque_nm * 1000.0
    sigma = 12 * torque / (b * work * (6 * 0.15 * d + b))
    allowable = ALLOWABLE_STRESS[material][load_type]
    ratio = sigma / allowable * 100
    key_h = parallel_key(d)['h']
    return {'b': b, 'h': key_h, 'L': length, 'work': work, 'sigma_p': sigma,
            'tolerances': tolerance_rows(
                b, key_h, length, 'N9', 'JS9', width_grade='h9',
                height_grade='h11', length_grade='h14'),
            'tol': {'b': 'h9', 'h': 'h11', 'L': 'h14'},
            'fit_shaft': 'N9', 'fit_hub': 'JS9', 'kind': kind,
            'standard': 'GB/T 1565-2003' if kind == '钩头' else 'GB/T 1564-2003',
            'allowable': allowable, 'ratio': ratio,
            'safe': ratio <= 100.0}


def spline_key(d):
    hits = [row for row in SPLINE_TABLE if abs(d - row[2]) <= 2]
    if not hits:
        hits = sorted(SPLINE_TABLE, key=lambda r: abs(d - r[2]))[:1]
    return hits[0]


def spline_check(d, torque_nm, length, heat='未热处理', usage='中等',
                 conn='静联接', centering='齿侧定心'):
    spec, N, ds, D, B = spline_key(d)
    h = (D - ds) / 2
    dm = (D + ds) / 2
    torque = torque_nm * 1000.0
    p = 2 * torque / (0.75 * N * h * length * dm)
    allow = {'静联接': {'未热处理': {'良好': 80, '中等': 60, '不良': 35},
                        '已热处理': {'良好': 120, '中等': 100, '不良': 40}},
             '动联接': {'未热处理': {'良好': 25, '中等': 20, '不良': 15},
                        '已热处理': {'良好': 40, '中等': 30, '不良': 25}}}
    allowable = allow.get(conn, allow['静联接']).get(heat, {}).get(usage, 60)
    ratio = p / allowable * 100
    return {'spec': spec, 'N': N, 'd': ds, 'D': D, 'B': B, 'h': h,
            'tolerances': fit_rows(B, spline_fit(centering)),
            'centering': centering, 'fit': spline_fit(centering),
            'L': length, 'p': p, 'allowable': allowable, 'ratio': ratio,
            'safe': ratio <= 100.0}


VERDICT_LABEL = {'suit': '适用', 'ok': '可用', 'no': '不适用'}


def recommend_key_type(d, load_type='静载荷', need_axial_move=False,
                       precision_req='一般', axial_force=False):
    """键型三态推荐：适用 / 可用 / 不适用。"""
    heavy = load_type == '冲击'
    recs = [{
        'type': 'parallel', 'name': '普通平键',
        'verdict': 'ok' if need_axial_move else 'suit',
        'reason': '对中性好、装拆方便；齿轮/带轮/蜗轮与轴的连接最常用。'
                  + ('轮毂需滑移时用导向平键更合适。' if need_axial_move else ''),
    }]
    if need_axial_move:
        recs.append({
            'type': 'guided', 'name': '导向平键', 'verdict': 'suit',
            'reason': '用螺钉固定在轴槽中，轮毂可沿轴向滑动。',
        })
    recs.append({
        'type': 'woodruff', 'name': '半圆键',
        'verdict': 'no' if heavy or d > 50 else 'ok',
        'reason': '键可绕几何中心摆动、便于装配；轴槽深、对轴削弱大，'
                  '不宜承受冲击重载。',
    })
    if axial_force and precision_req != '高' and not heavy:
        tv, tr = ('suit', '上下面为工作面，可同时传递扭矩并承受单向轴向力。')
    else:
        tv = 'no'
        tr = ('打入后轴与毂产生偏心，不适于严格对中、冲击载荷及高速传动。')
    recs.append({'type': 'taper', 'name': '普通楔键',
                 'verdict': tv, 'reason': tr})
    if heavy or precision_req == '高' or d > 50:
        sv = 'suit' if (precision_req == '高' or need_axial_move) else 'ok'
        recs.append({
            'type': 'spline', 'name': '矩形花键', 'verdict': sv,
            'reason': '多齿工作、承载高、定心与导向性好；制造较难、成本较高。',
        })
    order = {'suit': 0, 'ok': 1, 'no': 2}
    base = {'suit': 100, 'ok': 60, 'no': 10}
    for rec in recs:
        score = base[rec['verdict']]
        typ = rec['type']
        if typ == 'parallel':
            score += 10 if load_type != '冲击' else 0
        elif typ == 'guided':
            score += 15 if need_axial_move else 0
        elif typ == 'woodruff':
            score += 5 if d <= 30 else 0
            score -= 10 if heavy else 0
        elif typ == 'taper':
            score += 20 if axial_force else 0
            score -= 10 if precision_req == '高' else 0
        elif typ == 'spline':
            score += 15 if heavy or d > 50 else 0
            score += 10 if precision_req == '高' or need_axial_move else 0
        rec['score'] = score
    recs.sort(key=lambda x: (-x['score'], order[x['verdict']]))
    return recs


def choose_key_type(d, load_type='静载荷', need_axial_move=False,
                    precision='一般', axial_force=False):
    if need_axial_move:
        return 'guided', '导向平键', '轮毂需要轴向滑移，导向平键更合适。'
    if axial_force and precision != '高' and load_type != '冲击':
        return 'taper', '普通楔键', '需要承受单向轴向力，楔键可同时传扭。'
    if load_type == '冲击' or d > 50:
        return 'spline', '矩形花键', '载荷大、对中性高或轴径较大，花键更合适。'
    return 'parallel', '普通平键', '对中性好、装拆方便，最常用。'


def smart_design(d, torque_nm, hub_width=None, hub_material='钢',
                 load_type='静载荷', need_axial_move=False,
                 precision='一般', axial_force=False):
    """按工况选键型，并给出该键型的规格/校核。"""
    typ, name, reason = choose_key_type(d, load_type, need_axial_move,
                                        precision, axial_force)
    if typ in ('parallel', 'guided'):
        r = smart(d, torque_nm, hub_width, hub_material, load_type)
        r.update({'type': typ, 'type_name': name, 'reason': reason})
        return r
    if typ == 'woodruff':
        r = woodruff_check(d, torque_nm, hub_material, load_type)
        r.update({'type': typ, 'type_name': name, 'reason': reason})
        return r
    if typ == 'taper':
        b = parallel_key(d)['b']
        length = select_length(b, hub_width or 4 * b)
        r = taper_check(d, torque_nm, length, hub_material, load_type)
        r.update({'type': typ, 'type_name': name, 'reason': reason})
        return r
    spec, N, ds, D, B = spline_key(d)
    length = hub_width or 4 * B
    r = spline_check(d, torque_nm, length)
    r.update({'type': typ, 'type_name': name, 'reason': reason})
    return r


def parallel_check_manual(d, b, h, L, torque_nm, material='钢',
                          load_type='静载荷', key_type='A', fit='正常联结',
                          key_material='45钢'):
    """手动平键校核；A圆头/B方头/C单圆头。"""
    if min(d, b, h, L) <= 0:
        raise ValueError('平键参数必须大于 0')
    if key_type == 'A':
        work = max(1.0, L - b)
    elif key_type == 'C':
        work = max(1.0, L - b / 2)
    else:
        work = L
    torque = torque_nm * 1000.0
    sigma = 2 * torque / (d * (h / 2.0) * work)
    tau = 2 * torque / (d * b * work)
    allowable = ALLOWABLE_STRESS[material][load_type]
    ratio_p = sigma / allowable * 100
    tau_allow = KEY_MATERIALS.get(key_material, 60)
    ratio_t = tau / tau_allow * 100
    row = next((x for x in FITS if x[0] == fit), FITS[1])
    return {
        'd': d, 'b': b, 'h': h, 'L': L, 'work': work,
        'key_type': key_type, 'fit_name': row[0],
        'tol': dict(KEY_TOL),
        'fit_shaft': row[1], 'fit_hub': row[2],
        'tolerances': tolerance_rows(b, h, L, row[1], row[2]),
        'sigma_p': sigma, 'allowable_p': allowable, 'tau': tau,
        'allowable_tau': tau_allow, 'key_material': key_material,
        'ratio_p': ratio_p, 'ratio_t': ratio_t,
        'ratio': max(ratio_p, ratio_t),
        'safe': ratio_p <= 100 and ratio_t <= 100,
        'mark': '键%s %g×%g×%g GB/T 1096-2003' % (
            key_type, b, h, L),
    }


def taper_length(b, hub_width, kind='A'):
    """普通楔键/钩头楔键标准键长。"""
    if hub_width <= 0:
        raise ValueError('轮毂宽度必须大于 0')
    if kind == '钩头':
        target = hub_width * 1.1
        cand = [x for x in KEY_LENGTH_SERIES if x >= target]
        return min(cand) if cand else KEY_LENGTH_SERIES[-1]
    if hub_width < b + 8:
        raise ValueError('轮毂宽度过小，无法选楔键长度')
    cand = [x for x in KEY_LENGTH_SERIES if b <= x <= hub_width]
    return max(cand) if cand else None


def spline_fit(centering='齿侧定心'):
    return {'齿侧定心': 'H7/f7', '外径定心': 'H7/h6',
            '内径定心': 'H7/g6'}.get(centering, 'H7/f7')
