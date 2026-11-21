# -*- coding: utf-8 -*-
"""单位换算：完整工程单位表、角度度分秒和硬度换算。"""

from . import unit_data as _data


def category_names():
    """按原版顺序返回类别中文名。"""
    return tuple(_data.CATEGORIES[key]['name'] for key in _data.CAT_ORDER)


def _key(category):
    if category in _data.CATEGORIES:
        return category
    for key in _data.CAT_ORDER:
        if _data.CATEGORIES[key]['name'] == category:
            return key
    raise ValueError('未知类别：%s' % category)


def unit_entries(category):
    return _data.CATEGORIES[_key(category)]['units']


def unit_labels(category):
    """界面展示用完整名称，例如 'mm (毫米)'。"""
    return tuple(unit['name'] for unit in unit_entries(category))


def _short(name):
    return name.split(' ')[0].split(' (')[0]


def units(category):
    """兼容接口：返回短单位名（重复名称取首次出现）。"""
    result = []
    for unit in unit_entries(category):
        short = _short(unit['name'])
        if short not in result:
            result.append(short)
    return tuple(result)


def _index(category, name):
    entries = unit_entries(category)
    for i, unit in enumerate(entries):
        if unit['name'] == name:
            return i
    short = _short(name)
    for i, unit in enumerate(entries):
        if _short(unit['name']) == short:
            return i
    raise ValueError('单位 %s 不属于%s' % (name, category))


def convert(value, category, from_unit, to_unit):
    key = _key(category)
    try:
        result, _ = _data.convert(value, key, _index(category, from_unit),
                                  _index(category, to_unit))
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError('换算失败：%s' % exc)
    if result is None:
        raise ValueError('该硬度值超出换算表范围')
    return result


def format_value(value):
    return _data._fmt(value)


def formula(category, from_unit, to_unit):
    key = _key(category)
    if key == 'temp':
        return '温度按 °C / °F / K 仿射关系换算'
    if key == 'angle' and _short(from_unit) == '度分秒':
        return '度分秒：1° = 60′ = 3600″'
    if key == 'hardness':
        return '硬度按 HRC/HV/HBW/HS 对照表插值换算'
    entries = unit_entries(category)
    from_u = entries[_index(category, from_unit)]
    to_u = entries[_index(category, to_unit)]
    if from_u.get('factor') is None or to_u.get('factor') is None:
        return '查表换算'
    factor = from_u['factor'] / to_u['factor']
    return '1 %s = %.6g %s' % (_short(from_unit), factor, _short(to_unit))


# 兼容旧调用方：类别名到单位短名的映射
CATEGORIES = {name: list(units(name)) for name in category_names()}
