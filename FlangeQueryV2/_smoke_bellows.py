# -*- coding: utf-8 -*-
"""波纹管模块冒烟测试（offscreen）：U_bellows.csv 加载 + 筛选 + 详情/图形。"""
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


print('=== A. U_bellows.csv 文件结构 ===')
p = os.path.join(DATA_DIR, 'U_bellows.csv')
with open(p, encoding='utf-8-sig', newline='') as f:
    rows = list(csv.reader(f))
head, data = rows[0], rows[1:]
check(head == ['序号', 'DN', '接管规格', 'D_o', 'h', 'q', 'r', 'Lt', 'N', 'a'],
      '表头 = 序号/DN/接管规格/D_o/h/q/r/Lt/N/a -> ' + ','.join(head))
check(len(data) == 44, '数据行数 = 44（实际 %d）' % len(data))
check(all(len(r) == 10 for r in data), '所有行列数一致（10）')
dns = [r[1] for r in data]
check(len(set(dns)) == 44, 'DN 无重复（44 个唯一值）')
check(dns[0] == '50' and dns[-1] == '2800', 'DN 首行 50 / 末行 2800')
# 抽查放大核验过的易错单元格
ix = {h: i for i, h in enumerate(head)}
r4 = data[3]
check(r4[ix['DN']] == '100a' and r4[ix['接管规格']] == 'φ108×4',
      '第4行 = 100a / φ108×4')
r9 = data[8]
check(r9[ix['DN']] == '200' and r9[ix['D_o']] == '209', '第9行 DN200 Do=209')
r29 = data[28]
check(r29[ix['DN']] == '1000a' and r29[ix['D_o']] == '1004',
      '第29行 1000a Do=1004')
r44 = data[43]
check(r44[ix['DN']] == '2800' and r44[ix['a']] == '282.78',
      '第44行 DN2800 a=282.78')

print('=== B. main.py 常量与映射 ===')
check(any(k == 'bellows' for k, _ in main.FILTER_DEFS.items())
      or 'bellows' in main.FILTER_DEFS, 'FILTER_DEFS 含 bellows')
check(main.page_kind('U_bellows.csv') == 'bellows', "page_kind('U_bellows.csv') = bellows")
check(any(t[0] == '波纹管' for t in main.TABS), "TABS 含 '波纹管' 页签")
check(any(std.startswith('U形波纹管') for std, _ in main.PAGES),
      'PAGES 含 U形波纹管 分组')
check(os.path.exists(os.path.join(main.TPL_DIR, 'bellows.bmp')),
      'bellows.bmp 模板存在')

print('=== C. GUI 加载与交互 ===')
app = QApplication(sys.argv)
app.setStyle('Fusion')
w = main.MainWindow()

# 找到波纹管页签并点击
bix = next(i for i, (nm, _) in enumerate(main.TABS) if nm == '波纹管')
w.on_tab(bix)
loaded = 0
for i in range(w.tree.topLevelItemCount()):
    top = w.tree.topLevelItem(i)
    if top.isHidden():
        continue
    for j in range(top.childCount()):
        ch = top.child(j)
        meta = ch.data(0, Qt.UserRole)
        if not meta or meta[1] != 'U_bellows.csv':
            continue
        w.on_tree(ch, 0)
        n = w.table.rowCount()
        check(n == 44, '表格加载 44 行（实际 %d）' % n)
        check(w.cur_view == 'bellows', 'cur_view = bellows')
        # 表头含中文列名
        hdrs = [w.table.horizontalHeaderItem(c).text()
                for c in range(w.table.columnCount())]
        check('波谷外径 Do' in hdrs and '接管规格 dᵢ×S' in hdrs,
              '表头含中文列名: ' + ' | '.join(hdrs))
        # 选中 100a 行（第4行）
        w.table.selectRow(3)
        w.on_row()
        kv_labels = [w.kv.item(i, 0).text() for i in range(w.kv.rowCount())]
        check('公称直径 DN' in kv_labels and '波谷外径 Do (mm)' in kv_labels,
              '详情键值含中文字段: %d 项' % len(kv_labels))
        # 筛选：公称直径 = 100a
        cb = w.filter_widgets.get('DN')
        check(cb is not None, 'DN 筛选下拉存在')
        if cb is not None:
            cb.setCurrentIndex(list(cb.items()).index('100a')
                               if hasattr(cb, 'items')
                               else cb.findText('100a'))
            w.fill_table()
            check(w.table.rowCount() == 1, "筛选 DN=100a → 1 行（实际 %d）"
                  % w.table.rowCount())
            w.reset_filters()
        loaded += 1
check(loaded == 1, '波纹管子页加载 1 个（实际 %d）' % loaded)

print('\n=== 结果 ===')
if fails:
    print('有 %d 项失败:' % len(fails))
    for f in fails:
        print(' -', f)
    sys.exit(1)
else:
    print('全部通过 ✅')
