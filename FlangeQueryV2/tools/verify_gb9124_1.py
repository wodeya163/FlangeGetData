# -*- coding: utf-8 -*-
"""复核 Data/GBT9124_1_带颈对焊.csv 与 GB/T 9124.1-2019 PDF 表27–38。

真值来源：标准规范/GB_T_法兰系列/GB-T 9124.1-2019.pdf
用 pymupdf find_tables 结构化提取（比纯文本行解析更可靠），按表格 bbox
与"表NN PNxx 对焊"标题的 y 坐标关联，逐表确定 PN。

用法（受管 python + PYTHONPATH=pylibs）：
    python tools/verify_gb9124_1.py            # 只比对，输出差异
    python tools/verify_gb9124_1.py --fix      # 比对并按 PDF 修正 CSV

CSV 列: PN,DN,A1_A,A1_B,D,K,L,n,Th,C,N_A,N_B,S_min,H1_mean,R,H,密封面,RF_d,RF_f1
PDF 表列(15): DN,AⅠ,AⅡ,D,K,L,n,Th,C,H,NⅠ,NⅡ,Smin,H1,r
注意 CSV 的 N_A/N_B 存 NⅠ/NⅡ，H 列存 PDF 的 H（法兰高度）。
"""
import csv
import os
import re
import sys

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(os.path.dirname(ROOT), '标准规范', 'GB_T_法兰系列',
                   'GB-T 9124.1-2019.pdf')
CSV = os.path.join(ROOT, 'Data', 'GBT9124_1_带颈对焊.csv')

# CSV 前 16 列（后面 密封面/RF_d/RF_f1 是派生字段，不参与尺寸复核）
COLS = ['PN', 'DN', 'A1_A', 'A1_B', 'D', 'K', 'L', 'n', 'Th',
        'C', 'N_A', 'N_B', 'S_min', 'H1_mean', 'R', 'H']
# PDF 15 列 -> CSV 字段
PDF2CSV = ['DN', 'A1_A', 'A1_B', 'D', 'K', 'L', 'n', 'Th', 'C', 'H',
           'N_A', 'N_B', 'S_min', 'H1_mean', 'R']


def _clean(v):
    """规范化的单元格值：去空白，去掉 C 列 (xx)a 与数字后 a/b 角标附注。"""
    if v is None:
        return ''
    s = re.sub(r'\s+', '', str(v))
    s = re.sub(r'\(\d+\)a?$', '', s)   # 91(46)a -> 91
    s = re.sub(r'^(\d+)a$', r'\1', s)  # 8a -> 8（螺栓数角标）
    return s


def _num(v):
    """数值化用于比较（'2.0' 与 '2' 视为相等）。"""
    s = _clean(v)
    try:
        f = float(s)
        return str(int(f)) if f == int(f) else str(f)
    except ValueError:
        return s.lower()


def extract_pdf():
    """返回 {(PN, DN): {字段: 值}}，DN>600 的跳过。"""
    doc = pymupdf.open(PDF)
    truth = {}
    seen = {}
    for pno in range(43, 55):          # pdf page 44..55 (0-based 43..54)
        page = doc[pno]
        # 标题: (y, PN)
        titles = []
        for b in page.get_text('blocks'):
            txt = re.sub(r'\s', '', b[4])
            m = re.search(r'表(\d+)PN([\d.]+)对焊', txt)
            if m:
                titles.append((b[1], m.group(2)))
        titles.sort()
        # 表格: (y0, data)
        tables = []
        for t in page.find_tables().tables:
            rows = t.extract()
            if len(rows) < 5:
                continue
            tables.append((t.bbox[1], rows))
        tables.sort()
        for y0, rows in tables:
            # 归属到 y0 上方最近标题；若本页首表在首标题之上，属于上一页最后一张表
            pn = next((p for (ty, p) in reversed(titles) if ty < y0), None)
            if pn is None:
                # 页首表格：延续上一页最后出现的表（PN 由调用顺序维护）
                pn = extract_pdf._carry
            if not pn:
                continue
            extract_pdf._carry = pn
            # 数据行：前 4 行是表头
            for r in rows[4:]:
                ncol = len(r)
                if ncol < 13:
                    continue
                cells = [_clean(x) for x in r[:ncol]]
                if not re.match(r'^\d+$', cells[0]):
                    continue
                dn = int(cells[0])
                if dn > 600:
                    continue
                if ncol >= 15:
                    # 15 列：DN,AⅠ,AⅡ,D,K,L,n,Th,C,H,NⅠ,NⅡ,Smin,H1,r
                    rec = {c: cells[i] for i, c in enumerate(PDF2CSV)}
                elif ncol == 14:
                    # PN100/160：DN,AⅠ,AⅡ,D,K,L,n,Th,C,H,N,Smin,H1,r（N 单系列）
                    keys = ['DN', 'A1_A', 'A1_B', 'D', 'K', 'L', 'n', 'Th', 'C',
                            'H', 'N', 'S_min', 'H1_mean', 'R']
                    m = dict(zip(keys, cells))
                    m['N_A'] = m['N_B'] = m.pop('N')
                    rec = m
                else:
                    # PN250/320/400：DN,A,D,K,L,n,Th,C,H,N,Smin,H1,r（A/N 均单系列）
                    keys = ['DN', 'A', 'D', 'K', 'L', 'n', 'Th', 'C', 'H',
                            'N', 'S_min', 'H1_mean', 'R']
                    m = dict(zip(keys, cells))
                    m['A1_A'] = m['A1_B'] = m.pop('A')
                    m['N_A'] = m['N_B'] = m.pop('N')
                    rec = m
                rec['PN'] = pn
                key = (pn, str(dn))
                if key in truth:
                    seen['dup'] = seen.get('dup', 0) + 1
                truth[key] = rec
    return truth


extract_pdf._carry = None


def compare(truth, fix=False):
    with open(CSV, encoding='utf-8-sig', newline='') as fh:
        rows = list(csv.DictReader(fh))
    extras = [c for c in rows[0] if c not in COLS] if rows else []
    problems = []
    covered = set()
    for row in rows:
        key = (row['PN'], row['DN'])
        covered.add(key)
        std = truth.get(key)
        if std is None:
            problems.append((key, 'NO_STD', '', ''))
            continue
        for col in COLS[2:]:           # 跳过 PN,DN
            a, b = _num(row.get(col, '')), _num(std.get(col, ''))
            # N_B 在 PDF 为 None(空) 时，CSV 填 N_A 视为等价（系列Ⅱ缺失=同系列Ⅰ）
            if col == 'N_B' and b == '' and a == _num(std.get('N_A', '')):
                continue
            if a != b:
                problems.append((key, col, row.get(col, ''), std.get(col, '')))
                if fix:
                    row[col] = std[col]
    missing = sorted(set(truth) - covered)
    if fix:
        with open(CSV, 'w', encoding='utf-8-sig', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    return problems, missing, len(rows), len(truth)


def main():
    fix = '--fix' in sys.argv
    truth = extract_pdf()
    print('PDF 提取标准行:', len(truth), '  PN 分布:',
          {pn: sum(1 for k in truth if k[0] == pn)
           for pn in sorted({k[0] for k in truth}, key=float)})
    problems, missing, nrows, nstd = compare(truth, fix=fix)
    print('CSV 行数:', nrows)
    print('差异数:', len(problems))
    for key, col, got, exp in problems[:80]:
        print('  %-12s %-10s CSV=%-10s PDF=%s' % (str(key), col, got, exp))
    if len(problems) > 80:
        print('  ... 其余 %d 条' % (len(problems) - 80))
    print('PDF 有而 CSV 无:', missing[:30], '（共 %d）' % len(missing))
    if fix:
        print('已按 PDF 修正 CSV（保留 密封面/RF_d/RF_f1 派生列）')


if __name__ == '__main__':
    main()
