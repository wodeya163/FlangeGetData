# -*- coding: utf-8 -*-
"""页面生命周期：切树、填充表格、选中行联动。"""

import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidgetItem

from core.page_kind import page_kind
from core.review import review_for, source_note

logger = logging.getLogger('flangequery')


def on_tree(win, item, _col):
    from main import find_data, load_page_with_source
    meta = item.data(0, Qt.UserRole)
    if not meta:
        return
    win._save_header_state()
    win.cur_page = meta
    name, csvf, tpl, labels, std = meta[:5]
    win.cur_spec = meta[5] if len(meta) > 5 else None
    if getattr(win.cur_spec, 'kind', '') == 'weight':
        win.cur_row = None
        win.rows = []
        win.head = []
        win._clear_detail()
        win.t1.setText(name)
        win.t2.setText('重量计算 · 参数手动输入 · 单位 mm / m / kg')
        win.show_weight_page(getattr(win.cur_spec, 'subtype', 'pipe'))
        return
    if getattr(win.cur_spec, 'kind', '') == 'selection':
        win.cur_row = None
        win.rows = []
        win.head = []
        win._clear_detail()
        win.t1.setText(name)
        win.t2.setText('选型工具 · 中间输入 · 右侧结果')
        win.show_selection_page(getattr(win.cur_spec, 'subtype', 'unit'))
        return
    win.main_stack.setCurrentWidget(win.data_page)
    logger.info('加载页面：%s / %s（%s）', std, name, csvf)
    win.cur_kind = page_kind(csvf)
    win.cur_view = ('pipe' if win.cur_kind in ('pipe', 'gbt_pipe')
                    else 'fitting' if win.cur_kind == 'fitting'
                    else 'bellows' if win.cur_kind == 'bellows'
                    else 'gasket' if win.cur_kind.startswith('gasket')
                    else 'flange')
    path = find_data(csvf)
    head, win.rows, data_source = load_page_with_source(csvf, path, std)
    logger.info('数据来源：%s', data_source)
    win.head = [h for h in head if h]
    logger.info('数据行：%d，列：%d', len(win.rows), len(win.head))
    win.t1.setText('%s · %s' % (name, '请选择行'))
    note = source_note(std, csvf)
    win.t2.setText('%s · 尺寸单位：mm%s'
                   % (std, (' · ' + note) if note else ''))
    win._clear_detail()
    win.build_filters()
    win.fill_table()


def fill_table(win):
    from main import (BELLOWS_COLS, GASKET_KV, SHOW_COLS, NumItem,
                      _num_or_str)
    if not win.cur_page:
        return
    name, csvf, tpl, labels, std = win.cur_page[:5]
    rows = win._filtered_rows()
    if getattr(win, 'cur_view', 'flange') in ('pipe', 'fitting'):
        ab = 'D_o_A' in win.head
        dob = ('D_o_A', 'D_o_B') if ab else ('D_o',)
        names = {'DN': 'DN', 'DN2': 'NPS (in)',
                 'D_o': '外径 D_o', 'D_o_A': '外径 A', 'D_o_B': '外径 B'}
        cols = [(c, names.get(c, c)) for c in win.head]
    elif getattr(win, 'cur_view', 'flange') == 'bellows':
        cols = [(c, t) for c, t in BELLOWS_COLS if c in win.head]
    elif getattr(win, 'cur_view', 'flange') == 'gasket':
        order = ['DN', 'DN2', 'PN', 'Class', '型式', 'D1', 'D2', 'D3',
                 'T', 'b', 'P', 'A', 'H', 'B', 'C', 'r', '标准']
        cols = [(c, GASKET_KV.get(c, c)) for c in order if c in win.head]
        for c in win.head:
            if c not in order:
                cols.append((c, GASKET_KV.get(c, c)))
    else:
        cols = [(c, t) for c, t in SHOW_COLS if any(r.get(c) for r in rows)] \
            or [(c, t) for c, t in SHOW_COLS]
        known = {c for c, _ in SHOW_COLS} | {'PN', 'Class', 'DN', 'DN2'}
        for c in win.head:
            if c in known or c.startswith('_'):
                continue
            cols.append((c, c))
        head_extra = []
        if 'Class' in win.head:
            head_extra.append(('Class', 'Class'))
        if 'PN' in win.head:
            head_extra.append(('PN', 'PN'))
        cols = head_extra + [(c, t) for c, t in cols
                             if c not in ('PN', 'Class')]
    if not any(c == '复核状态' for c, _ in cols) and \
            any(r.get('复核状态') for r in rows):
        cols.insert(0, ('复核状态', '复核状态'))
    win.current_cols = [c for c, _ in cols]
    cap = '查询结果：<b>%s · %s</b>' % (name, std)
    note = source_note(std, csvf)
    if note:
        cap += '<br><span style="color:#a15c00">%s</span>' % note
    review = review_for(csvf, std)
    cap += ('<br><span style="color:#666">复核状态：%s · %s</span>'
            % (review['label'], review['source']))
    win.cap.setText(cap)
    win.count_lab.setText('共 %d 条 · 点击行查看图形与详情' % len(rows))
    win.table.setSortingEnabled(False)
    win.table.setUpdatesEnabled(False)
    win.table.clear()
    win.table.setColumnCount(len(cols))
    win.table.setHorizontalHeaderLabels([t for _, t in cols])
    win.table.setRowCount(len(rows))
    numeric = {'D', 'K', 'C', 'H', 'N_A', 'N_B', 'A1_A', 'A1_B', 'RF_d',
               'RF_f1', 'm_kg', 'D_o', 'D_o_A', 'D_o_B', 'DN2', 'n', 'L',
               'D1', 'D2', 'D3', 'T', 'b', 'P', 'A', 'B', 'r',
               '序号', 'h', 'q', 'Lt', 'N', 'a'}
    for i, r in enumerate(rows):
        for j, (c, _) in enumerate(cols):
            raw = str(r.get(c, '') or '-')
            if c in ('DN', 'PN', 'Class') or c in numeric \
                    or c.startswith('Sch') or c.startswith('S') \
                    or c in ('STD', 'XS', 'XXS'):
                it = NumItem(raw, _num_or_str(raw if raw != '-' else -1))
            else:
                it = QTableWidgetItem(raw)
            it.setData(Qt.UserRole, r)
            it.setTextAlignment(Qt.AlignCenter)
            if c == '复核状态':
                status = r.get('review_status', '')
                color = {'verified': '#e8f5e9', 'partial': '#f5f5f5',
                         'inferred': '#fff3cd', 'alias': '#ffe0b2'}.get(status)
                if color:
                    it.setBackground(QColor(color))
                it.setToolTip(str(r.get('数据来源', '')))
            win.table.setItem(i, j, it)
    win.table.setUpdatesEnabled(True)
    win.table.setSortingEnabled(True)
    dn_col = next((j for j, (c, _) in enumerate(cols) if c == 'DN'), None)
    if dn_col is not None:
        win.table.sortItems(dn_col, Qt.AscendingOrder)
    if len(rows) <= 1000:
        win.table.resizeColumnsToContents()
    else:
        for i in range(len(cols)):
            win.table.setColumnWidth(i, 90)
    win._restore_header_state(csvf)
    status_col = next((j for j, (c, _) in enumerate(cols)
                       if c == '复核状态'), None)
    if status_col is not None:
        win.table.setColumnWidth(status_col, 90)


def on_row(win):
    from main import (BELLOWS_COLS, BELLOWS_KV, GASKET_KV, KV_EXTRA,
                      KV_LABELS)
    if not win.cur_page:
        return
    index = win.table.currentRow()
    if index < 0:
        items = win.table.selectedItems()
        if not items:
            return
        row = items[0].data(Qt.UserRole)
    else:
        item = win.table.item(index, 0)
        if item is None:
            return
        row = item.data(Qt.UserRole)
    win.cur_row = row
    name, csvf, tpl, labels, std = win.cur_page[:5]
    dn = row.get('DN', '')
    pn = (row.get('Class') and ('Class ' + row['Class'])) \
        or row.get('PN', '') or ''
    if pn and not pn.upper().startswith(('PN', 'CLASS')):
        pn = 'PN' + pn
    win.t1.setText('%s · DN%s（当前选中）' % (name, dn))
    t2 = '%s · %s · 尺寸单位：mm' % (std, pn)
    note = source_note(std, csvf)
    if note:
        t2 += ' · ' + note
    row_label = str(row.get('复核状态', '') or '').strip()
    if row_label:
        t2 += ' · 本行复核：%s' % row_label
    if row.get('face_status') == 'missing':
        t2 += ' · 面型尺寸缺失，图形为近似'
    win.t2.setText(t2)
    win.card.show_page(tpl, labels, row,
                       '%s\n%s %s DN%s' % (std, name.split()[0], pn, dn), std)
    if getattr(win, 'cur_view', 'flange') in ('pipe', 'fitting'):
        ab = 'D_o_A' in win.head
        dob = ('D_o_A', 'D_o_B') if ab else ('D_o',)
        base = ['DN', 'DN2'] + list(dob)
        zh = {'H_45': '45°弯头 H', 'F_90LR': '90°弯头 F(长半径)',
              'F_90SR': '90°弯头 F(短半径)', 'P_180LR': '180° P(长半径)',
              'K_180SR': '180° K(短半径)', 'A_180LR': '180° 背至端 A(长)',
              'A_180SR': '180° 背至端 A(短)', 'C': '中心至端面 C',
              'H': '端面至端面 H', 'E': '管帽长度 E', 'E1': '长度 E1',
              'T_lim': 'E 极限壁厚', 'DN_s': '异径端 DN',
              'DN2_s': '异径端 NPS', 'D_o_A_s': '异径端外径 A',
              'D_o_B_s': '异径端外径 B'}
        kv_rows = [('DN', 'DN'), ('DN2', 'NPS (in)'),
                   (dob[0], '外径 A (mm)' if ab else '外径 (mm)')]
        if ab:
            kv_rows.append(('D_o_B', '外径 B (mm)'))
        kv_rows += [(c, zh.get(c, c)) for c in win.head if c not in base]
    elif getattr(win, 'cur_view', 'flange') == 'bellows':
        kv_rows = [(c, BELLOWS_KV.get(c, c)) for c, _ in BELLOWS_COLS
                   if str(row.get(c, '') or '').strip() not in ('', '-')]
    elif getattr(win, 'cur_view', 'flange') == 'gasket':
        kv_rows = [(c, GASKET_KV.get(c, c)) for c in win.head
                   if c in GASKET_KV
                   and str(row.get(c, '') or '').strip() not in ('', '-')]
    else:
        kv_rows = [(c, lab) for c, lab in KV_LABELS
                   if c in win.head
                   and str(row.get(c, '') or '').strip() not in ('', '-')]
        kv_rows += [(c, lab) for c, lab in KV_EXTRA.items()
                    if c in win.head
                    and str(row.get(c, '') or '').strip() not in ('', '-')]
    win.kv.set_rows(kv_rows, row)
    win.st_msg.setText('就绪')
    size = win.card.src_size
    size_text = '%d×%d' % size if size else '未知尺寸'
    win.st_tpl.setText('模板：%s (%s)' % (tpl, size_text))
    win.st_anchor.setText(
        '标注点：参数化矢量图' if getattr(win.card, '_vector', False)
        else ('标注点：WN 位图实测' if labels
              else '标注点：示意图（数值标注待逐类校准）'))
