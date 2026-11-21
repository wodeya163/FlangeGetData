# -*- coding: utf-8 -*-
"""导出控制器：当前筛选结果、选中行、当前行。"""

import os

from PyQt5.QtWidgets import QFileDialog, QMessageBox

from core.review import (attach_review, attach_source, review_for,
                         source_note)
from flange_export import resolve_export_columns, write_csv, write_xlsx

import logging

logger = logging.getLogger('flangequery')


def _safe_part(text):
    text = str(text).strip()
    for ch in '<>:"/\\|?*':
        text = text.replace(ch, '_')
    return text.strip(' .') or '未命名'


def export_selected(win):
    rows = win._selected_rows()
    if not rows:
        QMessageBox.information(win, '提示', '请先在表格中选择行')
        return
    if not win.cur_page:
        return
    base = os.path.splitext(win.cur_page[1])[0]
    export_rows(win, rows, '%s_选中%d行.csv' % (base, len(rows)), '选中行')


def export_all(win, show_cols):
    export_rows(win, win._filtered_rows(),
                win.cur_page[1] if win.cur_page else '导出.csv',
                '当前查询结果', show_cols)


def export_row(win):
    if not win.cur_row:
        QMessageBox.information(win, '提示', '请先在中间表选择一行规格')
        return
    if not win.cur_page:
        return
    base = os.path.splitext(win.cur_page[1])[0]
    export_rows(win, [win.cur_row],
                '%s_DN%s.csv' % (base, _safe_part(win.cur_row.get('DN', ''))),
                '当前选中行')


def export_rows(win, rows, default_fn, what, show_cols=None):
    if not rows:
        QMessageBox.information(win, '提示', '当前没有可导出的数据')
        return
    fn, selected = QFileDialog.getSaveFileName(
        win, '导出数据', default_fn,
        'CSV (*.csv);;Excel 工作簿 (*.xlsx)')
    if not fn:
        return
    lower = fn.lower()
    if lower.endswith('.xlsx'):
        pass
    elif lower.endswith('.csv'):
        if 'xlsx' in selected.lower():
            fn = fn[:-4] + '.xlsx'
    else:
        fn += '.xlsx' if 'xlsx' in selected.lower() else '.csv'
    note = source_note(win.cur_page[4], win.cur_page[1]) if win.cur_page else ''
    review = review_for(win.cur_page[1], win.cur_page[4]) \
        if win.cur_page else {'label': '', 'source': ''}
    rows = attach_source(rows, note)
    rows = attach_review(rows, review)
    fallback = [c for c, _ in (show_cols or [])]
    cols = resolve_export_columns(rows, win.current_cols, fallback)
    for extra in ('数据来源', '复核状态'):
        if any(extra in r for r in rows) and extra not in cols:
            cols.append(extra)
    if not cols:
        QMessageBox.warning(win, '导出失败', '没有可导出的列。')
        return
    try:
        if fn.lower().endswith('.xlsx'):
            write_xlsx(fn, rows, cols)
        else:
            write_csv(fn, rows, cols)
    except Exception as exc:
        logger.exception('导出失败')
        QMessageBox.critical(win, '导出失败', '写入文件失败：\n%s' % exc)
        return
    logger.info('导出%s：%d 行 -> %s（列：%s）',
                what, len(rows), fn, ','.join(cols))
    QMessageBox.information(win, '完成',
                            '已导出%s %d 行 → %s' % (what, len(rows), fn))
