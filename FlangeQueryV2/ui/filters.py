# -*- coding: utf-8 -*-
"""筛选条构建与过滤控制器。"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QComboBox, QLabel, QLineEdit, QPushButton)

from core.page_kind import row_schs, row_seals


def clear_filter_widgets(win):
    win._filter_timer.stop()
    for w in list(win.filter_widgets.values()):
        w.hide()
        w.deleteLater()
    win.filter_widgets = {}
    win.range_widgets = {}
    while win.frow.count():
        item = win.frow.takeAt(0)
        w = item.widget()
        if w is not None:
            w.hide()
            w.deleteLater()


def build_filters(win):
    from main import FILTER_DEFS, RANGE_FILTER_COLS, MultiCombo
    clear_filter_widgets(win)
    defs = FILTER_DEFS.get(getattr(win, 'cur_kind', 'hgt20592'), [])
    range_cols = RANGE_FILTER_COLS.get(getattr(win, 'cur_kind', ''), set())
    for col, lab, disp in defs:
        if col in range_cols:
            if col not in win.head:
                continue
            lb = QLabel(lab)
            lo = QLineEdit()
            hi = QLineEdit()
            lo.setPlaceholderText('最小')
            hi.setPlaceholderText('最大')
            for edit in (lo, hi):
                edit.setFixedWidth(64)
                edit.setStyleSheet('border:1px solid #c2c8cf;border-radius:4px;'
                                   'padding:3px 6px;font-size:12px;background:#fff;')
                edit.textChanged.connect(win._schedule_filter)
            win.frow.addWidget(lb)
            win.frow.addWidget(lo)
            win.frow.addWidget(QLabel('~'))
            win.frow.addWidget(hi)
            win.range_widgets[col] = (lo, hi)
            continue
        vals = enum_values(win, col, disp)
        if not vals:
            continue
        lb = QLabel(lab)
        if col == 'seal':
            cb = MultiCombo(vals)
            cb.changed.connect(win.on_filter_changed)
        else:
            cb = QComboBox()
            cb.addItems(['全部'] + vals)
            cb.currentTextChanged.connect(win.on_filter_changed)
        cb.setMinimumWidth(78)
        cb.setProperty('col', col)
        win.frow.addWidget(lb)
        win.frow.addWidget(cb)
        win.filter_widgets[col] = cb
    win.frow.addStretch(1)
    btn = QPushButton('重置筛选')
    btn.setProperty('class', 'tab')
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet('font-size:12px;color:#1f4e79;background:#eef3f8;'
                      'border:1px solid #c2c8cf;border-radius:4px;padding:3px 10px;')
    btn.clicked.connect(win.reset_filters)
    win.frow.addWidget(btn)


def enum_values(win, col, disp=None):
    from main import _sch_order, _inch_sort, sort_key_mixed
    rows = win.rows
    if not rows:
        return []
    if col == 'seal':
        s = set()
        for r in rows:
            s |= row_seals(r)
        order = ['RF 突面', 'RJ 环连接', 'FM/TG 凹凸/榫槽']
        return [v for v in order if v in s]
    if col == 'Sch':
        s = set()
        for r in rows:
            s |= row_schs(r)
        return sorted(s, key=_sch_order)
    if col not in win.head:
        return []
    s = {str(r.get(col, '')).strip() for r in rows}
    s = {v for v in s if v not in ('', '-')}
    if col in ('DN', 'DN2'):
        vals = sorted(s, key=_inch_sort)
    else:
        vals = sorted(s, key=sort_key_mixed)
    if disp:
        vals = [disp(v) for v in vals]
    return vals


def on_filter_changed(win, _text=''):
    win.fill_table()


def schedule_filter(win, _text=''):
    win._filter_timer.start()


def reset_filters(win):
    from main import MultiCombo
    for cb in win.filter_widgets.values():
        if isinstance(cb, MultiCombo):
            cb.set_values([])
            continue
        cb.blockSignals(True)
        cb.setCurrentIndex(0)
        cb.blockSignals(False)
    for lo, hi in win.range_widgets.values():
        for edit in (lo, hi):
            edit.blockSignals(True)
            edit.clear()
            edit.blockSignals(False)
    win.fill_table()


def match(win, r, col, val):
    if col == 'seal':
        return val in row_seals(r)
    if col == 'Sch':
        return val in row_schs(r)
    v = str(r.get(col, '')).strip()
    if col == 'PN':
        raw = r.get('PN', '').strip()
        shown = 'PN' + raw if raw and not raw.upper().startswith('PN') else raw
        return shown == val
    if col == 'Class':
        raw = r.get(col, '').strip()
        return ('Class ' + raw) == val or raw == val
    return v == val


def filtered_rows(win):
    from main import _col_label, _to_float, _in_range, fmt_num, MultiCombo
    rows = win.rows
    parts = []
    for col, cb in win.filter_widgets.items():
        if isinstance(cb, MultiCombo):
            vals = cb.values()
            if not vals:
                continue
            parts.append('%s = %s' % (_col_label(col), ' / '.join(vals)))
            rows = [r for r in rows if any(match(win, r, col, v) for v in vals)]
            continue
        v = cb.currentText()
        if v and v != '全部':
            parts.append('%s = %s' % (_col_label(col), v))
            rows = [r for r in rows if match(win, r, col, v)]
    for col, (lo_edit, hi_edit) in win.range_widgets.items():
        low = _to_float(lo_edit.text())
        high = _to_float(hi_edit.text())
        if low is None and high is None:
            continue
        rows = [r for r in rows if _in_range(r.get(col, ''), low, high)]
        parts.append('%s %s~%s' % (
            _col_label(col),
            '' if low is None else fmt_num(low),
            '' if high is None else fmt_num(high)))
    txt = ' · '.join(parts)
    win.chips.setText(('筛选条件：' + txt) if txt else '未设置筛选条件（全部规格）')
    return rows
