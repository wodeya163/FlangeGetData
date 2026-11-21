# -*- coding: utf-8 -*-
"""钢管/管件页签冒烟测试（offscreen）：确保 GB/T 17395-2024 三表正确加载、无异常。"""
import os
import sys

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
import main
import csv

DATA_DIR = os.path.join(main.APP_DIR, 'Data')
fails = []


def check(cond, msg):
    print(('  PASS ' if cond else '  FAIL ') + msg)
    if not cond:
        fails.append(msg)


def load_csv(p):
    with open(p, encoding='utf-8-sig', newline='') as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


print('=== A. GB/T 17395-2024 文件结构（长表） ===')
# 普通钢管
p1 = os.path.join(DATA_DIR, 'GB17395_普通钢管.csv')
h1, r1 = load_csv(p1)
check('DN' in h1 and 'D_o' in h1, '普通钢管: 含 DN/D_o')
check('系列' in h1, '普通钢管: 含 系列 列')
check('壁厚S(mm)' in h1 and '每米重量(kg/m)' in h1, '普通钢管: 含 壁厚S / 每米重量')
check(all(len(row) == len(h1) for row in r1), '普通钢管: 所有行与表头列数一致')
# 精密钢管
p2 = os.path.join(DATA_DIR, 'GB17395_精密钢管.csv')
h2, r2 = load_csv(p2)
check('D_o' in h2 and '壁厚S(mm)' in h2 and '每米重量(kg/m)' in h2,
      '精密钢管: 含 D_o / 壁厚S / 每米重量')
check('系列' not in h2, '精密钢管: 无 系列 列（定径管不标系列）')
check(all(len(row) == len(h2) for row in r2), '精密钢管: 列数一致')
# 不锈钢管
p3 = os.path.join(DATA_DIR, 'GB17395_不锈钢管.csv')
h3, r3 = load_csv(p3)
check('系列' in h3 and '标准尺寸' in h3, '不锈钢管: 含 系列 / 标准尺寸(●)')
check('每米重量(kg/m)' in h3, '不锈钢管: 含 每米重量')
dots = sum(1 for row in r3 if row[h3.index('标准尺寸')] == '●')
check(dots > 2000, '不锈钢管: 点阵 ● 总数=%d (>2000)' % dots)
check(all(len(row) == len(h3) for row in r3), '不锈钢管: 列数一致')
print('  普通 %d×%d | 精密 %d×%d | 不锈钢 %d×%d'
      % (len(r1), len(h1), len(r2), len(h2), len(r3), len(h3)))

print('=== B. GUI 钢管/管件页签加载 ===')
app = QApplication(sys.argv)
app.setStyle('Fusion')
w = main.MainWindow()

loaded = 0
for ti in range(len(main.TABS)):
    w.on_tab(ti)
    for i in range(w.tree.topLevelItemCount()):
        top = w.tree.topLevelItem(i)
        for j in range(top.childCount()):
            ch = top.child(j)
            meta = ch.data(0, Qt.UserRole)
            csvf = meta[1] if meta else None
            if csvf not in main.PIPE_CSVS and csvf not in main.FITTING_CSVS:
                continue
            try:
                w.on_tree(ch, 0)
                n = w.table.rowCount()
                if n == 0:
                    fails.append('空表: %s/%s' % (top.text(0), ch.text(0)))
                    print('  FAIL 空表: %s/%s' % (top.text(0), ch.text(0)))
                    continue
                w.table.selectRow(0)
                w.on_row()
                loaded += 1
                tag = ''
                if csvf in ('GB17395_普通钢管.csv', 'GB17395_精密钢管.csv',
                            'GB17395_不锈钢管.csv'):
                    tag = '  <<< GB/T 17395-2024'
                print('  PASS 加载: %s/%s (%d 行)%s'
                      % (top.text(0), ch.text(0), n, tag))
            except Exception as e:
                fails.append('异常: %s/%s %s' % (top.text(0), ch.text(0), e))
                print('  FAIL 异常: %s/%s %s' % (top.text(0), ch.text(0), e))

print('  共加载 %d 个钢管/管件子页' % loaded)

print('\n=== 结果 ===')
if fails:
    print('有 %d 项失败:' % len(fails))
    for f in fails:
        print(' -', f)
    sys.exit(1)
else:
    print('全部通过 ✅')
