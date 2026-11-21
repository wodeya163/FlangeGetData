# -*- coding: utf-8 -*-
"""GB/T 12459 管件壁厚表：按 DN + 壁厚系列查询。"""

import csv
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, 'Data', 'GB12459_GBT13401.csv')
_CACHE = None


def wall_table():
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    table = {}
    if not os.path.isfile(PATH):
        _CACHE = table
        return table
    with io.open(PATH, encoding='utf-8-sig', newline='') as fh:
        rd = csv.DictReader(fh)
        for row in rd:
            dn = str(row.get('DN', '')).strip()
            if not dn:
                continue
            vals = {}
            for key, value in row.items():
                if not key or key in ('DN', 'DN2', 'D_o_A', 'D_o_B'):
                    continue
                try:
                    number = float(str(value).strip())
                except (TypeError, ValueError):
                    continue
                if number > 0:
                    vals[key] = number
            table[dn] = vals
    _CACHE = table
    return table


def available_series():
    table = wall_table()
    if not table:
        return ('Sch40',)
    seen = []
    for vals in table.values():
        for key in vals:
            if key not in seen:
                seen.append(key)
    return tuple(seen)


def wall_for(row, series='Sch40'):
    """返回管件壁厚 mm；T_lim 优先，其次壁厚表。"""
    if series == 'T_lim':
        try:
            return float(str(row.get('T_lim', '')).strip())
        except (TypeError, ValueError):
            return 0.0
    dn = str(row.get('DN', '')).strip()
    vals = wall_table().get(dn, {})
    try:
        return float(vals.get(series, 0.0))
    except (TypeError, ValueError):
        return 0.0
