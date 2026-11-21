# -*- coding: utf-8 -*-
"""螺栓拧紧力矩：按螺栓类型、规格、强度等级和场景取标准推荐值。"""

from core.torque_data import (HEX_BOLT, SCENARIOS, SELF_TAPPING,
                              SOCKET_CAP)

TYPES = {
    'hex': '六角头螺栓',
    'socket': '内六角圆柱头螺钉',
    'self_tap': '自攻螺钉',
}

TYPE_TABLE = {
    'hex': HEX_BOLT,
    'socket': SOCKET_CAP,
    'self_tap': SELF_TAPPING,
}


def sizes(bolt_type):
    table = TYPE_TABLE.get(bolt_type, {})
    return list(table.keys())


def grades(bolt_type, size):
    if bolt_type == 'self_tap':
        return []
    table = TYPE_TABLE.get(bolt_type, {}).get(size, {})
    return list(table.keys())


def materials(bolt_type, size):
    if bolt_type != 'self_tap':
        return []
    return list(TYPE_TABLE.get('self_tap', {}).get(size, {}).keys())


def torque(bolt_type, size, grade, material=None):
    if bolt_type == 'self_tap':
        table = TYPE_TABLE['self_tap'].get(size, {})
        return table.get(material)
    table = TYPE_TABLE.get(bolt_type, {}).get(size, {})
    return table.get(grade)


def scenario(value, name):
    """返回场景系数后的 (min, recommended, max, note)。"""
    item = SCENARIOS.get(name)
    if item is None or value is None:
        return None
    f = item['factor']
    return (round(value[0] * f[0], 1),
            round(value[1] * f[1], 1),
            round(value[2] * f[2], 1),
            item['note'])


def wrench_range(value):
    """按推荐力矩给出扳手量程建议。"""
    if value is None or value <= 0:
        return ''
    low = max(1.0, value * 0.6)
    high = value * 1.5
    return '%.0f – %.0f N·m' % (low, high)
