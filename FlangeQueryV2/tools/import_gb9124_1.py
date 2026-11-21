# -*- coding: utf-8 -*-
"""从 GB/T 9124.1-2019 PDF 转录对焊法兰 PN6–PN160 数据（DN≤600）。

表 28 PN6、29 PN10、30 PN16、31 PN25、32 PN40、33 PN63、34 PN100、35 PN160。
表 27（PN2.5）与表 36–38（PN250/320/400）暂不纳入。
"""

import csv
import os
import re

import pdfplumber

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF = os.path.join(os.path.dirname(ROOT), '标准规范', 'GB_T_法兰系列',
                   'GB-T 9124.1-2019.pdf')
OUT = os.path.join(ROOT, 'Data', 'GBT9124_1_带颈对焊.csv')

HEAD = ['PN', 'DN', 'A1_A', 'A1_B', 'D', 'K', 'L', 'n', 'Th',
        'C', 'N_A', 'N_B', 'S_min', 'H1_mean', 'R', 'H']

ROW = re.compile(
    r'^(\d+)\s+([\d.]+)\s+([\d.]+|-)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)'
    r'\s+(M\d+)\s+(.+)$')


def parse_line(line, pn):
    if pn is None:
        return None
    m = ROW.match(line.strip())
    if not m:
        return None
    dn = int(m.group(1))
    if dn > 600:
        return None
    rest = [p for p in m.group(9).split() if re.match(r'^[\d.]+$', p)]
    if len(rest) < 6:
        return None
    c, h, n = rest[0], rest[1], rest[2]
    s_min, h1, r = rest[-3], rest[-2], rest[-1]
    return [pn, str(dn), m.group(2), m.group(3), m.group(4), m.group(5),
            m.group(6), m.group(7), m.group(8), c, n, n, s_min, h1, r, h]


def parse_page(text, start_pn, switches=None):
    switches = switches or {}
    rows = []
    pn = start_pn
    for line in text.splitlines():
        compact = re.sub(r'\s+', '', line)
        hit = next((v for k, v in switches.items() if k in compact), 'no')
        if hit != 'no':
            pn = hit
            continue
        row = parse_line(line, pn)
        if row:
            rows.append(row)
    return rows


def main():
    with pdfplumber.open(PDF) as pdf:
        pages = {i: pdf.pages[i - 1].extract_text() or ''
                 for i in (46, 47, 48, 49, 50, 51, 52, 53, 54)}

    rows = []
    rows += parse_page(pages[46], '6')
    rows += parse_page(pages[47], '10')

    # 页48：顶部是 PN10 的 DN450–600，表30 起为 PN16 DN10–20
    for line in pages[48].splitlines():
        if '表30PN16' in re.sub(r'\s+', '', line):
            break
        row = parse_line(line, '10')
        if row and int(row[1]) >= 450:
            rows.append(row)
    for line in pages[48].splitlines():
        row = parse_line(line, '16')
        if row and int(row[1]) <= 20:
            rows.append(row)

    rows += parse_page(pages[49], '16')
    rows += parse_page(pages[50], '25')
    rows += parse_page(pages[51], '40', {'表33PN63': '63'})
    rows += parse_page(pages[52], '63', {'表34PN100': '100'})
    rows += parse_page(pages[53], '100', {'表35PN160': '160'})
    rows += parse_page(pages[54], '160', {'表36PN250': None})

    unique = {}
    for row in rows:
        unique[(row[0], int(row[1]))] = row
    rows = [unique[k] for k in sorted(unique,
                                      key=lambda x: (float(x[0]), x[1]))]

    with open(OUT, 'w', encoding='utf-8', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow(HEAD)
        writer.writerows(rows)
    print('written', OUT, 'rows', len(rows))
    print('PN:', sorted({r[0] for r in rows}, key=float))
    for pn in sorted({r[0] for r in rows}, key=float):
        print(pn, sum(1 for r in rows if r[0] == pn))


if __name__ == '__main__':
    main()
