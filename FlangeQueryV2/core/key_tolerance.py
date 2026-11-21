# -*- coding: utf-8 -*-
"""键与键槽的极限偏差。

键宽/键高/键长的公差按 ISO 286（GB/T 1800）IT 等级计算；
键槽宽度按 GB/T 1095-2003 的 N9 / JS9 / P9 / H9 / D10 表值取用。
单位内部统一为 μm，显示时换算为 mm。
"""

from vendor.tolerance.data.it_tolerance import get_it_tolerance
from vendor.tolerance.data.limit_deviations import get_deviations


# GB/T 1095-2003 普通平键键槽宽度极限偏差（μm）
# 键宽 b 的分组与表值：N9, JS9, P9, H9, D10 = (上偏差, 下偏差)
KEYWAY_WIDTH_TOL = [
    (3, {'N9': (0, -4), 'JS9': (12.5, -12.5), 'P9': (-6, -31),
         'H9': (25, 0), 'D10': (60, 20)}),
    (6, {'N9': (0, -30), 'JS9': (15, -15), 'P9': (-12, -42),
         'H9': (30, 0), 'D10': (78, 30)}),
    (10, {'N9': (0, -36), 'JS9': (18, -18), 'P9': (-15, -51),
          'H9': (36, 0), 'D10': (98, 40)}),
    (18, {'N9': (0, -43), 'JS9': (21.5, -21.5), 'P9': (-18, -61),
          'H9': (43, 0), 'D10': (120, 50)}),
    (25, {'N9': (0, -52), 'JS9': (26, -26), 'P9': (-22, -74),
          'H9': (52, 0), 'D10': (149, 65)}),
    (50, {'N9': (0, -62), 'JS9': (31, -31), 'P9': (-26, -88),
          'H9': (62, 0), 'D10': (180, 80)}),
    (80, {'N9': (0, -74), 'JS9': (37, -37), 'P9': (-32, -106),
          'H9': (74, 0), 'D10': (220, 100)}),
    (100, {'N9': (0, -87), 'JS9': (43.5, -43.5), 'P9': (-37, -124),
           'H9': (87, 0), 'D10': (260, 120)}),
]


def _it(size, grade):
    if size is None or size <= 0:
        return None
    digits = ''.join(ch for ch in str(grade) if ch.isdigit())
    value = get_it_tolerance(float(size), digits)
    return None if value is None or value < 0 else float(value)


def _mm(value):
    text = '%.4f' % (value / 1000.0)
    return text.rstrip('0').rstrip('.')


def keyway_deviations(width, code):
    """返回键槽宽度的 (上偏差, 下偏差)，单位 μm。"""
    code = (code or '').replace('JS', 'JS').replace('js', 'JS')
    for limit, table in KEYWAY_WIDTH_TOL:
        if width <= limit:
            return table.get(code)
    return None


def key_deviations(size, grade):
    """键（轴类）公差：h 系列，上偏差 0，下偏差 -IT。"""
    it = _it(size, grade)
    return None if it is None else (0, -it)


def hole_deviations(size, grade):
    """孔类公差：H 系列，下偏差 0，上偏差 +IT。"""
    it = _it(size, grade)
    return None if it is None else (it, 0)


def _row(label, basic, code, dev):
    if dev is None:
        return None
    upper, lower = dev
    return {
        'label': label,
        'basic': basic,
        'code': code,
        'upper': upper,
        'lower': lower,
        'upper_mm': _mm(upper),
        'lower_mm': _mm(lower),
        'span_mm': _mm(abs(upper - lower)),
    }


def tolerance_rows(b, h, length, fit_shaft='N9', fit_hub='JS9',
                   width_grade='h8', height_grade='h11',
                   length_grade='h14', length_label='键长 L',
                   include_key_length=True):
    """生成键和键槽的极限偏差行（μm 与 mm 同时保留）。"""
    rows = [
        _row('键宽 b', b, width_grade, key_deviations(b, width_grade)),
        _row('键高 h', h, height_grade, key_deviations(h, height_grade)),
    ]
    if include_key_length:
        rows.append(_row(length_label, length, length_grade,
                         key_deviations(length, length_grade)))
    rows.append(_row('轴槽宽', b, fit_shaft, keyway_deviations(b, fit_shaft)))
    rows.append(_row('毂槽宽', b, fit_hub, keyway_deviations(b, fit_hub)))
    return [row for row in rows if row]


def fit_rows(size, fit_code):
    """花键等配合代号（如 H7/f7）的极限偏差行。"""
    parts = (fit_code or '').split('/')
    if len(parts) != 2:
        return []
    hole_code, shaft_code = parts
    rows = []
    hole = get_deviations(hole_code, float(size))
    shaft = get_deviations(shaft_code, float(size))
    if hole:
        rows.append(_row('内花键宽', size, hole_code, hole))
    if shaft:
        rows.append(_row('外花键宽', size, shaft_code, shaft))
    return rows


def format_tolerance_rows(rows):
    """把公差行格式化为结果区的多行文本。"""
    if not rows:
        return ''
    lines = ['公差（mm）：']
    for row in rows:
        lines.append('%s %s %s：%s / %s' % (
            row['label'], ('%g' % row['basic']) if row['basic'] else '',
            row['code'], row['upper_mm'], row['lower_mm']))
    return '\n'.join(lines)
