# -*- coding: utf-8 -*-
"""金属材料重量计算（移植自 gdjoss/metal-material-calculator）。

支持板材、圆棒、方棒、六角棒、圆管、方管、角钢，以及
GB/T 706 槽钢/工字钢理论重量查表。
"""

import math

from core.metal_weight_data import (CHANNEL_TABLE, IBEAM_TABLE,
                                    MATERIALS)

STEEL_DENSITY = 7.85  # g/cm³，GB/T 706 理论重量基准

SHAPES = [
    {'id': 'plate', 'name': '板材', 'formula': 'V = t × w × l',
     'params': [('t', '厚度'), ('w', '宽度'), ('l', '长度')],
     'defaults': {'t': 10.0, 'w': 100.0, 'l': 1000.0}},
    {'id': 'round-bar', 'name': '圆棒', 'formula': 'V = π/4 × d² × l',
     'params': [('d', '直径'), ('l', '长度')],
     'defaults': {'d': 50.0, 'l': 1000.0}},
    {'id': 'square-bar', 'name': '方棒', 'formula': 'V = a² × l',
     'params': [('a', '边长'), ('l', '长度')],
     'defaults': {'a': 50.0, 'l': 1000.0}},
    {'id': 'hex-bar', 'name': '六角棒', 'formula': 'V = (√3/2) × s² × l',
     'params': [('s', '对边距'), ('l', '长度')],
     'defaults': {'s': 30.0, 'l': 1000.0}},
    {'id': 'round-tube', 'name': '圆管',
     'formula': 'V = π/4 × (D² − (D−2t)²) × l',
     'params': [('D', '外径'), ('t', '壁厚'), ('l', '长度')],
     'defaults': {'D': 50.0, 't': 3.0, 'l': 1000.0}},
    {'id': 'square-tube', 'name': '方管',
     'formula': 'V = (a² − (a−2t)²) × l',
     'params': [('a', '外边长'), ('t', '壁厚'), ('l', '长度')],
     'defaults': {'a': 50.0, 't': 3.0, 'l': 1000.0}},
    {'id': 'angle', 'name': '角钢',
     'formula': 'V ≈ (A + B − t) × t × l',
     'params': [('A', '长边'), ('B', '短边'), ('t', '壁厚'),
                ('l', '长度')],
     'defaults': {'A': 50.0, 'B': 50.0, 't': 5.0, 'l': 1000.0}},
    {'id': 'channel', 'name': '槽钢',
     'formula': '查表重量 = GB/T 706 理论重量 × 长度',
     'table': 'channel',
     'params': [('spec', '型号', 'select'), ('l', '长度')],
     'defaults': {'spec': '10#', 'l': 1000.0}},
    {'id': 'ibeam', 'name': '工字钢',
     'formula': '查表重量 = GB/T 706 理论重量 × 长度',
     'table': 'ibeam',
     'params': [('spec', '型号', 'select'), ('l', '长度')],
     'defaults': {'spec': '16#', 'l': 1000.0}},
]

SHAPE_BY_ID = {s['id']: s for s in SHAPES}
MATERIAL_BY_ID = {m[0]: (m[1], m[2]) for m in MATERIALS}
UNIT_TO_CM = {'mm': 0.1, 'cm': 1.0, 'm': 100.0}


def table_for(shape):
    if shape.get('table') == 'channel':
        return CHANNEL_TABLE
    if shape.get('table') == 'ibeam':
        return IBEAM_TABLE
    return None


def calculate(shape_id, material_id, dims, unit='mm', quantity=1,
              price_per_kg=0.0, custom_density=None):
    """计算单件/合计重量。dims 数值使用 unit 指定的单位。"""
    shape = SHAPE_BY_ID.get(shape_id)
    if shape is None:
        raise ValueError('未知型材')
    if unit not in UNIT_TO_CM:
        raise ValueError('未知尺寸单位')
    if material_id == 'custom':
        try:
            density = float(custom_density)
        except (TypeError, ValueError):
            density = 0.0
        if density <= 0:
            raise ValueError('自定义密度需大于 0')
        material_name = '自定义材料'
    else:
        item = MATERIAL_BY_ID.get(material_id)
        if item is None:
            raise ValueError('未知材质')
        material_name, density = item

    table = table_for(shape)
    values = {}
    if table is not None:
        spec = str(dims.get('spec', '')).strip()
        if spec not in table:
            raise ValueError('请选择型号')
        values['spec'] = spec
        for key in ('l',):
            value = float(dims.get(key, 0))
            if value <= 0:
                raise ValueError('长度需大于 0')
            values[key] = value * UNIT_TO_CM[unit]
        length_cm = values['l']
        kgm_steel = table[spec][1]
        factor = density / STEEL_DENSITY
        per_meter = kgm_steel * factor
        weight = per_meter * (length_cm / 100.0)
        volume_cm3 = weight * 1000.0 / density
        formula = ('m = %s × L × (ρ / 7.85)　（GB/T 706 基准）'
                   % table[spec][1])
        detail = '型号 %s，理论重量 %.3f kg/m（钢），按材质密度换算' % (
            table[spec][0], kgm_steel)
    else:
        for key, _label in shape['params']:
            value = float(dims.get(key, 0))
            if value <= 0:
                raise ValueError('%s 需大于 0' % _label)
            values[key] = value * UNIT_TO_CM[unit]
        _validate(shape_id, values)
        volume_cm3 = _volume(shape_id, values)
        weight = volume_cm3 * density / 1000.0
        length_cm = values.get('l', 0)
        per_meter = weight / (length_cm / 100.0) if length_cm > 0 else 0.0
        formula = shape['formula']
        detail = '体积 %.4f cm³，密度 %.2f g/cm³' % (volume_cm3, density)

    qty = int(quantity) if quantity else 1
    qty = max(1, qty)
    total = weight * qty
    price = total * price_per_kg if price_per_kg and price_per_kg > 0 else None
    return {
        'shape': shape['name'],
        'material': material_name,
        'density': density,
        'mass': weight,
        'total': total,
        'quantity': qty,
        'per_meter': per_meter,
        'volume': volume_cm3 / 1_000_000.0,  # m³
        'volume_cm3': volume_cm3,
        'price': price,
        'formula': formula,
        'detail': detail,
    }


def _validate(shape_id, d):
    if shape_id in ('round-tube',) and d['t'] * 2 >= d['D']:
        raise ValueError('壁厚需小于外径的一半')
    if shape_id in ('square-tube',) and d['t'] * 2 >= d['a']:
        raise ValueError('壁厚需小于外边长的一半')
    if shape_id == 'angle' and (d['t'] >= d['A'] or d['t'] >= d['B']):
        raise ValueError('壁厚需小于角钢边长')


def _volume(shape_id, d):
    if shape_id == 'plate':
        return d['t'] * d['w'] * d['l']
    if shape_id == 'round-bar':
        return math.pi / 4.0 * d['d'] ** 2 * d['l']
    if shape_id == 'square-bar':
        return d['a'] ** 2 * d['l']
    if shape_id == 'hex-bar':
        return math.sqrt(3) / 2.0 * d['s'] ** 2 * d['l']
    if shape_id == 'round-tube':
        return (math.pi / 4.0 * (d['D'] ** 2 - (d['D'] - 2 * d['t']) ** 2)
                * d['l'])
    if shape_id == 'square-tube':
        return (d['a'] ** 2 - (d['a'] - 2 * d['t']) ** 2) * d['l']
    if shape_id == 'angle':
        return (d['A'] + d['B'] - d['t']) * d['t'] * d['l']
    raise ValueError('未知型材')
