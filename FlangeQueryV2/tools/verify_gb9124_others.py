# -*- coding: utf-8 -*-
"""复核 GB/T 9124.1-2019 除带颈对焊外的其余法兰型式。

真值来源：标准规范/GB_T_法兰系列/GB-T 9124.1-2019.pdf
当前程序 GB/T 9124.1 页签中，除 WN 外均复用 HG/T 20592 CSV。
本脚本用 pymupdf find_tables() 提取 PDF 表 8–91（整体/螺纹/带颈平焊/
承插焊/板式平焊/对焊环松套/平焊环松套/法兰盖），与在用 CSV 的公共尺寸
字段逐项比对，输出差异；--fix 生成独立的 GBT9124_1_<型式>.csv（保留
HG/T 原有派生列，只按 PDF 覆盖公共尺寸列）。

用法：
    python tools/verify_gb9124_others.py
    python tools/verify_gb9124_others.py --fix
"""
import csv
import os
import re
import sys

import pymupdf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(os.path.dirname(ROOT), '标准规范', 'GB_T_法兰系列',
                   'GB-T 9124.1-2019.pdf')
DATA = os.path.join(ROOT, 'Data')

# 表格号 -> PN（表46/47 一表含两个 PN，需复制）
TABLE_PN = {}
for t, pn in [(8, '2.5'), (9, '6'), (10, '10'), (11, '16'), (12, '25'),
              (13, '40'), (14, '63'), (15, '100'), (16, '160'),
              (17, '250'), (18, '320'), (19, '400')]:
    TABLE_PN[t] = [pn]
for t, pn in [(20, '6'), (21, '10'), (22, '16'), (23, '25'), (24, '40'),
              (25, '63'), (26, '100')]:
    TABLE_PN[t] = [pn]
for t, pn in [(27, '2.5'), (28, '6'), (29, '10'), (30, '16'), (31, '25'),
              (32, '40'), (33, '63'), (34, '100'), (35, '160'),
              (36, '250'), (37, '320'), (38, '400')]:
    TABLE_PN[t] = [pn]
for t, pn in [(39, '6'), (40, '10'), (41, '16'), (42, '25'), (43, '40'),
              (44, '63'), (45, '100')]:
    TABLE_PN[t] = [pn]
TABLE_PN[46] = ['10', '16']
TABLE_PN[47] = ['25', '40']
for t, pn in [(48, '63'), (49, '100')]:
    TABLE_PN[t] = [pn]
for t, pn in [(50, '2.5'), (51, '6'), (52, '10'), (53, '16'), (54, '25'),
              (55, '40'), (56, '63'), (57, '100')]:
    TABLE_PN[t] = [pn]
for t, pn in [(58, '10'), (59, '16'), (60, '25'), (61, '40'), (62, '63')]:
    TABLE_PN[t] = [pn]
for t, pn in [(63, '6'), (64, '10'), (65, '16'), (66, '25'), (67, '40')]:
    TABLE_PN[t] = [pn]
for t, pn in [(68, '2.5'), (69, '6'), (70, '10'), (71, '16'), (72, '25'),
              (73, '40')]:
    TABLE_PN[t] = [pn]
for t, pn in [(74, '2.5'), (75, '10'), (76, '16')]:
    TABLE_PN[t] = [pn]
for t, pn in [(77, '2.5'), (78, '10'), (79, '16')]:
    TABLE_PN[t] = [pn]
for t, pn in [(80, '2.5'), (81, '6'), (82, '10'), (83, '16'), (84, '25'),
              (85, '40'), (86, '63'), (87, '100'), (88, '160'),
              (89, '250'), (90, '320'), (91, '400')]:
    TABLE_PN[t] = [pn]

# family -> (CSV, 表号范围, PDF列->CSV字段, 首行数据最少列数)
FAMILIES = {
    '整体': ('HGT20592_整体.csv', range(8, 20),
             {0: 'DN', 1: 'D', 2: 'K', 3: 'L', 4: 'n', 5: 'Th', 6: 'C',
              7: 'N', 8: 'R'}, 9),
    '螺纹': ('HGT20592_螺纹.csv', range(20, 27),
             {0: 'DN', 1: 'A1', 2: 'D', 3: 'K', 4: 'L', 5: 'n', 6: 'Th',
              7: 'C', 8: 'H', 9: 'N', 10: 'r'}, 11),
    '带颈平焊': ('HGT20592_带颈平焊.csv', range(39, 46),
                 {0: 'DN', 1: 'A1_A', 2: 'A1_B', 3: 'D', 4: 'K', 5: 'L',
                  6: 'n', 7: 'Th', 8: 'C', 9: 'H', 10: 'N_A', 11: 'N_B',
                  12: 'r', 13: 'B1_A', 14: 'B1_B'}, 15),
    '承插焊': ('HGT20592_承插焊.csv', range(46, 50),
               {0: 'DN', 1: 'A1_A', 2: 'A1_B', 3: 'D', 4: 'K', 5: 'L',
                6: 'n', 7: 'Th', 8: 'C', 9: 'H', 10: 'N', 11: 'r',
                12: 'B1_A', 13: 'B1_B', 14: 'B2_A', 15: 'B2_B',
                16: 'T'}, 17),
    '板式平焊': ('HGT20592_板式平焊.csv', range(50, 58),
                 {0: 'DN', 1: 'A1_A', 2: 'A1_B', 3: 'D', 4: 'K', 5: 'L',
                  6: 'n', 7: 'Th', 8: 'C', 9: 'RF_d', 10: 'RF_f1',
                  11: 'B1_A', 12: 'B1_B'}, 13),
    '对焊环松套': ('HGT20592_对焊环松套.csv', range(58, 68),
                   {0: 'DN', 1: 'A1_A', 2: 'A1_B', 3: 'D', 4: 'K', 5: 'L',
                    6: 'n', 7: 'Th', 8: 'C', 9: 'B1_A', 10: 'B1_B'}, 19),
    '平焊环松套': ('HGT20592_平焊环松套.csv', range(68, 74),
                   {0: 'DN', 1: 'A1_A', 2: 'A1_B', 3: 'D', 4: 'K', 5: 'L',
                    6: 'n', 7: 'Th', 8: 'C', 9: 'B1_A', 10: 'B1_B',
                    15: 'F'}, 16),
    '法兰盖': ('HGT20592_法兰盖.csv', range(80, 92),
               {0: 'DN', 1: 'D', 2: 'K', 3: 'L', 4: 'n', 5: 'Th', 6: 'C'}, 7),
}

# 特殊映射：PDF 字段名 -> CSV 字段名（按 family）
FIELD_ALIAS = {
    '整体': {'N': 'N', 'R': 'R'},
    '螺纹': {'N': 'N', 'r': 'R'},
    '带颈平焊': {'N_A': 'N_A', 'N_B': 'N_B', 'r': 'R'},
    '承插焊': {'N': 'N', 'r': 'R'},
    '板式平焊': {},
    '对焊环松套': {},
    '平焊环松套': {},
    '法兰盖': {},
}


def clean(v):
    if v is None:
        return ''
    s = re.sub(r'\s+', '', str(v))
    # "40(36)a" / "30(26)a"：括号为原标准旧厚度，按 GB/T 9124.1 表注取括号外主值
    return re.sub(r'\(\d+\)[a-z]?$', lambda m: '', s)


def norm(v):
    s = clean(v).replace(',', '.')
    s = re.sub(r'\(\d+\)a?$', '', s)
    s = re.sub(r'^(\d+)a$', r'\1', s)
    s = re.sub(r'\*+$', '', s)
    try:
        f = float(s)
        return str(int(f)) if f == int(f) else str(f)
    except ValueError:
        return s.lower()


def extract_pdf():
    """返回 {family: {(PN, DN): {字段:值}}}。"""
    doc = pymupdf.open(PDF)
    # 一页内：标题 y -> (表号, 是否续表)
    out = {f: {} for f in FAMILIES}
    carry = {}          # 表号 -> 最近 PN
    for pno in range(len(doc)):
        page = doc[pno]
        titles = []
        for b in page.get_text('blocks'):
            txt = clean(b[4])
            m = re.search(r'表(\d+)(?:\(续\))?', txt)
            if not m:
                continue
            tno = int(m.group(1))
            if tno not in TABLE_PN:
                continue
            # 标题可能写 "PN10、PN16"，需逐个 PN 取出
            found = re.findall(r'PN\s*([\d.]+)', txt)
            pns = found or TABLE_PN[tno]
            titles.append((b[1], tno, pns, '(续)' in txt))
        titles.sort()
        tables = sorted((t.bbox[1], t.extract())
                        for t in page.find_tables().tables)
        for y0, rows in tables:
            cand = next((t for t in reversed(titles) if t[0] < y0 - 2), None)
            if cand is None:
                # 本页首个表格位于标题之上：延续上一页最后一张表
                if extract_pdf.last is None:
                    continue
                tno, pns, is_cont = extract_pdf.last
            else:
                _, tno, pns, is_cont = cand
            if tno not in TABLE_PN:
                continue
            if is_cont:
                pns = carry.get(tno, TABLE_PN[tno])
            carry[tno] = pns
            extract_pdf.last = (tno, pns, is_cont)
            family = next((f for f, (_, rng, _, _) in FAMILIES.items()
                           if tno in rng), None)
            if family is None:
                continue
            _, _, cmap, mincol = FAMILIES[family]
            # 跳过表头：首列为纯数字的即为数据行
            for r in rows:
                if len(r) < mincol or not re.match(r'^\d+$', clean(r[0])):
                    continue
                dn = int(clean(r[0]))
                for pn in pns:
                    rec = {}
                    for idx, field in cmap.items():
                        if idx < len(r):
                            rec[field] = clean(r[idx])
                    rec['PN'] = norm(pn)
                    rec['DN'] = str(dn)
                    out[family][(norm(pn), str(dn))] = rec
    doc.close()
    return out


extract_pdf.last = None


def extract_face():
    """GB/T 9124.1 表6：{(PN, DN): (RF_d, RF_f1)}。"""
    doc = pymupdf.open(PDF)
    rows = doc[22].find_tables().tables[0].extract()
    pn_idx = {'2.5': 1, '6': 2, '10': 3, '16': 4, '25': 5}
    face, f1_last = {}, '2'
    for r in rows:
        if not r or not re.match(r'^\d+$', clean(r[0])):
            continue
        dn = str(int(clean(r[0])))
        if clean(r[7]):
            f1_last = clean(r[7])
        for pn, idx in list(pn_idx.items()) + [('40+', 6)]:
            d = clean(r[idx]) if idx < len(r) else ''
            if d in ('', '—', '-'):
                continue
            key_pn = pn if pn != '40+' else '40'
            face[(key_pn, dn)] = (d, f1_last)
        for pn in ('63', '100', '160', '250', '320', '400'):
            d = clean(r[6]) if len(r) > 6 else ''
            if d not in ('', '—', '-'):
                face[(pn, dn)] = (d, f1_last)
    doc.close()
    return face


def csv_rows(fname):
    with open(os.path.join(DATA, fname), encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))


def compare(truth, fix=False, compare_hg=False):
    """比对 PDF 真值与数据表。

    默认复核程序实际使用的 GBT9124_1_<型式>.csv（应零差异）；
    --compare-hg 比对 HG/T 20592 原始表，展示两标准间的固有差异；
    --fix 以 PDF 为真值重建 GB 专用表——
    · 公共尺寸字段按 PDF 覆盖；
    · 密封面 d/f1 按 PDF 表6 覆盖；
    · HG/T 独有的派生列（质量、LSR 等）沿用原行，PDF 新增行留空；
    · PDF 未列的 (PN,DN) 从 GB 表剔除（HG/T 页签仍保留原数据）。
    """
    report = {}
    face = extract_face() if fix else {}
    for family, (fname, _, cmap, _) in FAMILIES.items():
        gb_name = 'GBT9124_1_' + family + '.csv'
        actual = fname if (fix or compare_hg) else gb_name
        if not os.path.exists(os.path.join(DATA, actual)):
            actual = fname
        rows = csv_rows(actual)
        headers = list(rows[0].keys())
        base = truth[family]
        alias = FIELD_ALIAS[family]
        problems, covered = [], set()
        by_key = {}
        for row in rows:
            key = (norm(row.get('PN', '')), norm(row.get('DN', '')))
            covered.add(key)
            by_key[key] = row
            std = base.get(key)
            if std is None:
                problems.append((key, 'NO_STD', '', ''))
                continue
            for idx, field in cmap.items():
                if field in ('PN', 'DN'):
                    continue
                csvf = alias.get(field, field)
                a = norm(row.get(csvf, ''))
                b = norm(std.get(field, ''))
                # N_B 在 PDF 无系列Ⅱ时按系列Ⅰ处理
                if (field == 'N_B' and not b
                        and a == norm(std.get('N_A', ''))):
                    continue
                if a and b and a != b:
                    problems.append((key, csvf, row.get(csvf, ''),
                                     std.get(field, '')))
        missing = sorted(set(base) - covered)
        report[family] = (actual, rows, problems, missing, len(base))
        if not fix:
            continue
        out_rows = []
        for key in sorted(base, key=lambda k: (float(k[0]), int(k[1]))):
            std = base[key]
            row = dict(by_key.get(key) or {h: '' for h in headers})
            row['PN'] = key[0]
            row['DN'] = key[1]
            for idx, field in cmap.items():
                if field in ('PN', 'DN'):
                    continue
                csvf = alias.get(field, field)
                if field in std and std[field] != '':
                    row[csvf] = std[field]
            if 'RF_d' in headers:
                fd = face.get(key)
                if fd:
                    row['RF_d'] = fd[0]
                    row['RF_f1'] = fd[1]
            if '密封面' in headers and not row.get('密封面'):
                row['密封面'] = 'RF'
            out_rows.append({h: row.get(h, '') for h in headers})
        out = 'GBT9124_1_' + family + '.csv'
        with open(os.path.join(DATA, out), 'w', encoding='utf-8-sig',
                  newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=headers)
            w.writeheader()
            w.writerows(out_rows)
        report[family] = (out, out_rows, problems, missing, len(base))
    return report


def main():
    fix = '--fix' in sys.argv
    compare_hg = '--compare-hg' in sys.argv
    truth = extract_pdf()
    report = compare(truth, fix=fix, compare_hg=compare_hg)
    total = 0
    for family, (fname, rows, problems, missing, nstd) in report.items():
        total += len(problems)
        print('\n=== %s : %s %d 行 / PDF %d 行 / 差异 %d / PDF多出 %d'
              % (family, fname, len(rows), nstd, len(problems), len(missing)))
        for key, col, got, exp in problems[:25]:
            print('  %-12s %-10s CSV=%-10s PDF=%s' % (str(key), col, got, exp))
        if len(problems) > 25:
            print('  ... 其余 %d 条' % (len(problems) - 25))
        if missing:
            print('  PDF 多出(前10):', missing[:10])
    print('\n总差异数:', total)
    if fix:
        print('已生成 GBT9124_1_<型式>.csv（公共尺寸按 PDF 覆盖，派生列保留）')
    elif compare_hg:
        print('以上为 HG/T 20592 与 GB/T 9124.1 的标准间固有差异，非数据错误')
    else:
        print('复核对象：程序实际使用的 GBT9124_1_<型式>.csv')
        print('复核结论：' + ('通过，PDF 公共尺寸零差异' if total == 0
                             else '存在 %d 处差异，需按 PDF 修正' % total))


if __name__ == '__main__':
    main()
