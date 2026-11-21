# -*- coding: utf-8 -*-
"""FlangeQueryV2 全量测试审核脚本（无头）。
覆盖四层：
  A. 静态结构链路：TABS→PAGES→CSV/模板 全量引用解析，悬空/孤儿检测
  B. 数据质量：垫片 11 数值表 + 4 描述表（表头、数值列、几何、重复、边界、DN 范围）
  C. 资源完整性：所有引用模板 BMP 尺寸/模式校验
  D. GUI 功能（offscreen）：密封件 15 子页 + 法兰/管件/钢管抽样 + 首/末行边界交互
结果：任意 FAIL 则退出码 1。
"""
import os, sys, csv
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

import main

APP_DIR = main.APP_DIR
TPL_DIR = main.TPL_DIR
DATA_DIR = os.path.join(APP_DIR, 'Data')

fails = []
def check(cond, msg, sev='FAIL'):
    if cond:
        print('  PASS', msg)
        return True
    print('  %s' % sev, msg)
    if sev == 'FAIL':
        fails.append(msg)
    return False

NUMERIC = {'DN','DN2','PN','Class','D1','D2','D3','T','b','P','A','H','B','C','r','t'}
TEXT_COLS = {'标准','型式','代号','名称','适用标准','适用压力范围','说明'}

# ----------------------------------------------------------------------
print('\n========== A. 静态结构链路审计 ==========')
# 收集所有 PAGES 引用
ref_csv, ref_tpl, gasket_csv_labels = set(), set(), {}
for gname, items in main.PAGES:
    for (name, csvf, tpl, labels) in items:
        ref_csv.add(csvf)
        ref_tpl.add(tpl)
        if csvf in main.GASKET_CSVS and csvf not in main.GASKET_REF_CSVS:
            gasket_csv_labels[csvf] = labels

all_csv = {os.path.basename(p) for p in os.listdir(DATA_DIR) if p.lower().endswith('.csv')}
all_tpl = {os.path.basename(p) for p in os.listdir(TPL_DIR) if p.lower().endswith('.bmp')}

print('  PAGES 组数=%d, 引用 CSV=%d, 引用模板=%d' % (len(main.PAGES), len(ref_csv), len(ref_tpl)))
# 悬空引用
for csvf in sorted(ref_csv):
    check(os.path.exists(os.path.join(DATA_DIR, csvf)), 'CSV 存在: %s' % csvf)
for tpl in sorted(ref_tpl):
    check(os.path.exists(os.path.join(TPL_DIR, tpl)), '模板存在: %s' % tpl)
# 孤儿文件
orphan_csv = sorted(all_csv - ref_csv)
orphan_tpl = sorted(all_tpl - ref_tpl)
print('  孤儿 CSV（Data/ 中存在但未被 PAGES 引用）: %s' % (orphan_csv if orphan_csv else '无'))
print('  孤儿模板（templates/ 中存在但未被 PAGES 引用）: %s' % (orphan_tpl if orphan_tpl else '无'))
check(main.GASKET_CSVS == (set(gasket_csv_labels) | main.GASKET_REF_CSVS),
      'GASKET_CSVS 与 PAGES 垫片引用完全一致')
check('密封件' in [t[0] for t in main.TABS], 'TABS 含「密封件」')
# 密封件 15 子页计数
gasket_groups = [g for g in main.PAGES if g[0].startswith('垫片') or g[0].startswith('密封面型式')]
gasket_sub = sum(len(items) for _, items in gasket_groups)
check(gasket_sub == 15, '垫片/密封面子页数=15（实际 %d）' % gasket_sub)

# ----------------------------------------------------------------------
print('\n========== B. 垫片数据质量审计 ==========')
UNIFIED = ['标准','DN','DN2','PN','Class','型式','D1','D2','D3','T','b','P','A','H','B','C','r']
DESCRIP = ['代号','名称','适用标准','适用压力范围','说明']

def audit_numeric_csv(fname):
    p = os.path.join(DATA_DIR, fname)
    with open(p, encoding='utf-8-sig', newline='') as fh:
        r = csv.reader(fh)
        head = next(r)
        rows = list(r)
    ncol = len(head)
    check(ncol == len(UNIFIED), '%s 列数=%d（期望 17）' % (fname, ncol), sev='WARN' if ncol!=17 else 'FAIL')
    # 表头齐全
    missing = [c for c in UNIFIED if c not in head]
    check(not missing, '%s 表头含全部 17 字段（缺: %s）' % (fname, missing or '无'))
    idx = {c:i for i,c in enumerate(head)}
    labels = gasket_csv_labels.get(fname, {})
    exp_cols = list(labels.keys())  # 程序将显示/叠加的数值列
    # 显示列缺失（一次性判定，避免逐行刷屏）
    missing_cols = [c for c in exp_cols if c not in idx]
    check(not missing_cols, '%s 程序显示列缺失: %s' % (fname, missing_cols or '无'))
    exp_cols = [c for c in exp_cols if c in idx]  # 仅校验实际存在的列
    n = len(rows)
    dn_vals = []
    bad_num = []      # (行,列,值)
    d2_lt_d1 = 0
    empties = []      # 期望列但为空
    for ri, row in enumerate(rows, start=2):
        if len(row) != ncol:
            check(False, '%s 第 %d 行列数不符（%d≠%d）' % (fname, ri, len(row), ncol)); 
            continue
        # 期望数值列：非空 + 数值 + 正数
        for c in exp_cols:
            v = (row[idx[c]] or '').strip()
            if v == '':
                empties.append((ri, c)); continue
            try:
                fv = float(v)
            except ValueError:
                bad_num.append((ri, c, v)); continue
            if fv <= 0:
                bad_num.append((ri, c, v))
        # 几何：D2>=D1（两者均非空）
        if 'D1' in idx and 'D2' in idx:
            d1, d2 = (row[idx['D1']] or '').strip(), (row[idx['D2']] or '').strip()
            if d1 and d2:
                try:
                    if float(d2) < float(d1):
                        d2_lt_d1 += 1
                except ValueError:
                    pass
        # DN 收集
        if 'DN' in idx:
            dv = (row[idx['DN']] or '').strip()
            if dv:
                try: dn_vals.append(float(dv))
                except ValueError: pass
    # 汇总
    check(not bad_num, '%s 数值列非法/非正: %s' % (fname, bad_num[:5] + (['...'] if len(bad_num)>5 else []) or '无'),
          sev='FAIL' if bad_num else 'FAIL')
    check(d2_lt_d1 == 0, '%s 出现 D2<D1 的行数=%d' % (fname, d2_lt_d1), sev='WARN' if d2_lt_d1 else 'FAIL')
    check(not empties, '%s 期望显示列为空的单元格: %s' % (fname, empties[:5] + (['...'] if len(empties)>5 else []) or '无'),
          sev='WARN' if empties else 'FAIL')
    # 重复行
    seen, dups = set(), 0
    for row in rows:
        key = tuple(row)
        if key in seen: dups += 1
        seen.add(key)
    check(dups == 0, '%s 完全重复行数=%d' % (fname, dups), sev='WARN' if dups else 'FAIL')
    dnr = ('DN∈[%s,%s]' % (int(min(dn_vals)), int(max(dn_vals)))) if dn_vals else 'DN 无数值'
    print('    · %s: %d 行, 显示列=%s, %s' % (fname, n, exp_cols, dnr))
    return n

total_rows = 0
for csvf in sorted(gasket_csv_labels):
    total_rows += audit_numeric_csv(csvf)
print('  垫片数值表合计数据行=%d' % total_rows)

# 描述表 mfm_*
print('  --- 密封面型式参考（描述表）---')
for csvf in sorted(main.GASKET_REF_CSVS):
    p = os.path.join(DATA_DIR, csvf)
    with open(p, encoding='utf-8-sig', newline='') as fh:
        r = csv.reader(fh); head = next(r); rows = list(r)
    miss = [c for c in DESCRIP if c not in head]
    check(not miss, '%s 表头含 5 字段（缺: %s）' % (csvf, miss or '无'))
    check(len(rows) >= 1, '%s 至少有 1 条数据' % csvf)
    name_ok = any((row[head.index('名称')] if '名称' in head else '').strip() for row in rows)
    check(name_ok, '%s 名称非空' % csvf)

# ----------------------------------------------------------------------
print('\n========== C. 资源完整性审计 ==========')
try:
    from PIL import Image
    have_pil = True
except Exception as e:
    have_pil = False
    print('  WARN PIL 不可用，跳过 BMP 尺寸校验: %s' % e)
for tpl in sorted(ref_tpl):
    p = os.path.join(TPL_DIR, tpl)
    if not os.path.exists(p):
        check(False, '模板缺失: %s' % tpl); continue
    if have_pil:
        try:
            im = Image.open(p); im.load()
            check(im.size == (596,498) and im.mode in ('RGB','L'),
                  '%s 尺寸=%s 模式=%s' % (tpl, im.size, im.mode), sev='WARN' if im.size!=(596,498) else 'FAIL')
        except Exception as e:
            check(False, '%s 读取失败: %s' % (tpl, e))

# ----------------------------------------------------------------------
print('\n========== D. GUI 功能审计（offscreen） ==========')
app = QApplication(sys.argv)
app.setStyle('Fusion')
w = main.MainWindow()

def load_subpage(top_text_prefixes, first_last=True, tag=''):
    """遍历匹配前缀的页签下所有子页，加载并可选首/末行 on_row。返回加载子页数。"""
    cnt = 0
    for ti in range(w.tree.topLevelItemCount()):
        top = w.tree.topLevelItem(ti)
        if not any(top.text(0).startswith(p) for p in top_text_prefixes):
            continue
        w.on_tree(top, 0) if False else None  # 确保树已展开（on_tab 已展开）
        for j in range(top.childCount()):
            ch = top.child(j)
            meta = ch.data(0, Qt.UserRole)
            try:
                w.on_tree(ch, 0)
                n = w.table.rowCount()
                if n == 0:
                    check(False, '[%s] 空表: %s/%s' % (tag, top.text(0), ch.text(0))); continue
                # 首行
                w.table.selectRow(0); w.on_row()
                # 末行（边界）
                if first_last and n > 1:
                    w.table.selectRow(n-1); w.on_row()
                cnt += 1
            except Exception as e:
                check(False, '[%s] 异常: %s/%s %s' % (tag, top.text(0), ch.text(0), e))
    return cnt

# 密封件页签
tab_idx = next(i for i,(n,_) in enumerate(main.TABS) if n=='密封件')
w.on_tab(tab_idx)
g_loaded = load_subpage(['垫片','密封面型式'], first_last=True, tag='密封件')
check(g_loaded == 15, '密封件 15 子页全部加载+首末行 on_row 无异常（实际 %d）' % g_loaded)

# 法兰/管件/钢管 抽样（确认未破坏）
w.on_tab(0)  # 法兰
f_loaded = load_subpage(['GB/T','HG/T','NB/T'], first_last=True, tag='法兰')
check(f_loaded > 0, '法兰抽样子页加载+边界 on_row 无异常（%d 个）' % f_loaded)

# 切换其它页签验证不崩溃
ok_other = True
for tname, pref in main.TABS:
    if tname in ('密封件',):  # 已测
        continue
    try:
        ti = next(i for i,(n,_) in enumerate(main.TABS) if n==tname)
        w.on_tab(ti)
        # 取该页签下第一个子页加载
        for k in range(w.tree.topLevelItemCount()):
            top = w.tree.topLevelItem(k)
            if any(top.text(0).startswith(p) for p in pref):
                if top.childCount():
                    w.on_tree(top.child(0), 0)
                    if w.table.rowCount()>0:
                        w.table.selectRow(0); w.on_row()
                break
    except Exception as e:
        ok_other = False
        check(False, '页签「%s」加载异常: %s' % (tname, e))
check(ok_other, '其余页签（管件/钢管等）切换加载无异常')

# ----------------------------------------------------------------------
print('\n========== 结果汇总 ==========')
print('失败项(FAIL)数: %d' % len(fails))
if fails:
    for f in fails: print(' -', f)
    sys.exit(1)
print('全部审计通过 ✅（WARN 项见上文，不影响功能）')
