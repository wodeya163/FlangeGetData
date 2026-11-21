# -*- coding: utf-8 -*-
"""无头冒烟测试（QT_QPA_PLATFORM=offscreen）：
1. 结构校验：TABS 含「密封件」且前缀正确；PAGES 含 8 标准 + 密封面型式参考；
   所有垫片子页的 CSV 与模板图均存在。
2. 交互校验：切换到「密封件」页签，逐子页加载 → 中间表有行 → 选中首行 → on_row 不抛错。
"""
import os
import sys

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

import main

APP_DIR = main.APP_DIR
TPL_DIR = main.TPL_DIR
DATA_DIR = os.path.join(APP_DIR, 'Data')

fails = []
def check(cond, msg):
    if cond:
        print('  PASS', msg)
    else:
        print('  FAIL', msg)
        fails.append(msg)


print('=== 1. 结构校验 ===')
tab_names = [t[0] for t in main.TABS]
check('密封件' in tab_names, 'TABS 含「密封件」')
for name, pref in main.TABS:
    if name == '密封件':
        check(pref == ['垫片', '密封面型式'], '密封件 前缀 = [垫片, 密封面型式]')

gasket_groups = [g for g in main.PAGES if g[0].startswith('垫片') or g[0].startswith('密封面型式')]
check(len(gasket_groups) == 9, 'PAGES 含 9 个垫片/密封面组（8 标准 + 参考），实际 %d' % len(gasket_groups))

gasket_csvs = []
for gname, items in gasket_groups:
    for (name, csvf, tpl, labels) in items:
        gasket_csvs.append(csvf)
        csv_path = os.path.join(DATA_DIR, csvf)
        check(os.path.exists(csv_path), 'CSV 存在: %s' % csvf)
        tpl_path = os.path.join(TPL_DIR, tpl)
        check(os.path.exists(tpl_path), '模板存在: %s' % tpl)

check(main.GASKET_CSVS == set(gasket_csvs), 'GASKET_CSVS 与 PAGES 完全对应')
check('gasket_pn' in main.FILTER_DEFS and 'gasket_class' in main.FILTER_DEFS
      and 'gasket_ref' in main.FILTER_DEFS, 'FILTER_DEFS 含 gasket_pn/class/ref')

print('=== 2. page_kind 校验 ===')
check(main.page_kind('HGT20606_RF.csv') == 'gasket_pn', '20606_RF → gasket_pn')
check(main.page_kind('HGT20627.csv') == 'gasket_class', '20627 → gasket_class')
check(main.page_kind('mfm_RJ.csv') == 'gasket_ref', 'mfm_RJ → gasket_ref')

print('=== 3. 交互校验（offscreen GUI） ===')
app = QApplication(sys.argv)
app.setStyle('Fusion')
w = main.MainWindow()

# 找到 密封件 tab 索引
tab_idx = next(i for i, (n, _) in enumerate(main.TABS) if n == '密封件')
w.on_tab(tab_idx)

checked = 0
for i in range(w.tree.topLevelItemCount()):
    top = w.tree.topLevelItem(i)
    if not top.text(0).startswith('垫片') and not top.text(0).startswith('密封面型式'):
        continue
    for j in range(top.childCount()):
        ch = top.child(j)
        meta = ch.data(0, Qt.UserRole)
        try:
            w.on_tree(ch, 0)
            nrows = w.table.rowCount()
            if nrows == 0:
                fails.append('空表: %s/%s' % (top.text(0), ch.text(0)))
                print('  FAIL 空表: %s/%s' % (top.text(0), ch.text(0)))
                continue
            w.table.selectRow(0)
            w.on_row()
            checked += 1
            print('  PASS 加载: %s/%s (%d 行)' % (top.text(0), ch.text(0), nrows))
        except Exception as e:
            fails.append('异常: %s/%s %s' % (top.text(0), ch.text(0), e))
            print('  FAIL 异常: %s/%s %s' % (top.text(0), ch.text(0), e))

print('  交互校验通过 %d 个子页' % checked)

print('=== 4. 法兰/管件页签未被破坏 ===')
w.on_tab(0)  # 法兰
fcount = sum(w.tree.topLevelItem(k).childCount() for k in range(w.tree.topLevelItemCount())
             if w.tree.topLevelItem(k).text(0).startswith(('GB/T', 'HG/T', 'NB/T')))
check(fcount > 0, '法兰相关组仍有子页（%d）' % fcount)

print('\n=== 结果 ===')
if fails:
    print('有 %d 项失败:' % len(fails))
    for f in fails:
        print(' -', f)
    sys.exit(1)
else:
    print('全部通过 ✅')
