# -*- coding: utf-8 -*-
"""查询解析与跨页搜索（无 Qt 依赖）。"""


def _to_float(value):
    try:
        return float(str(value).strip().replace(',', '.'))
    except (TypeError, ValueError):
        return None


def split_query(text, head):
    """把查询拆成 (列=值 条件, 自由关键字)。"""
    dims, free = [], []
    keys = sorted(head, key=len, reverse=True)
    for token in str(text).split():
        if '=' in token:
            col, value = token.split('=', 1)
            col, value = col.strip(), value.strip()
            if col in head and value:
                dims.append((col, value))
            else:
                free.append(token)
            continue
        matched = False
        for key in keys:
            if len(token) <= len(key):
                continue
            if token[:len(key)].lower() != key.lower():
                continue
            value = token[len(key):]
            if _to_float(value) is None:
                continue
            dims.append((key, value))
            matched = True
            break
        if not matched:
            free.append(token)
    return dims, free


def _cell_matches(cell, value):
    text = str(cell).strip()
    if text in ('', '-'):
        return False
    left, right = _to_float(text), _to_float(value)
    if left is not None and right is not None:
        return abs(left - right) < 1e-6
    return text.lower() == str(value).strip().lower()


def row_matches_query(row, head, dims, free, std, name):
    for col, value in dims:
        if col not in row or not _cell_matches(row.get(col, ''), value):
            return False
    if free:
        blob = ' '.join([std, name]
                        + [str(row.get(k, '')) for k in head]).lower()
        for term in free:
            if term.lower() not in blob:
                return False
    return True


def search_all(query, pages, find_data, load_csv, limit=300, cache=None):
    """跨全部标准页搜索，返回 [(标准, 类型, CSV, 行, 条件摘要)]。"""
    results = []
    seen_csv = set()
    cache = {} if cache is None else cache
    for std, items in pages:
        for name, csvf, _tpl, _labels in items:
            if not csvf or not csvf.lower().endswith('.csv'):
                continue
            if csvf in seen_csv:
                continue
            path = find_data(csvf)
            if path is None:
                continue
            if csvf not in cache:
                cache[csvf] = load_csv(path)
            head, rows = cache[csvf]
            dims, free = split_query(query, head)
            if not dims and not free:
                continue
            for row in rows:
                if row_matches_query(row, head, dims, free, std, name):
                    summary = ' '.join('%s=%s' % (c, v) for c, v in dims)
                    results.append((std, name, csvf, row, summary))
                    if len(results) >= limit:
                        return results
            seen_csv.add(csvf)
    return results
