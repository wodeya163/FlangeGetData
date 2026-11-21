# -*- coding: utf-8 -*-
"""补齐 GB/T 9124.1 对焊 PN2.5 与 PN250/320/400。

在现有 PN6–160 表基础上追加；高压表为单列外径（仅 A 系列）。
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

TWO = re.compile(r'^(\d+)\s+([\d.]+)\s+([\d.]+|-)\s+(.+)$')
ONE = re.compile(r'^(\d+)\s+([\d.]+)\s+(.+)$')


def _num_tokens(text):
    return [p for p in text.split() if re.match(r'^M\d+$', p)
            or re.match(r'^[\d.]+$', p)]


def parse_two(text, pn):
    rows = []
    for line in text.splitlines():
        m = TWO.match(line.strip())
        if not m:
            continue
        dn = int(m.group(1))
        if dn > 600:
            continue
        vals = _num_tokens(m.group(4))
        if len(vals) < 11:
            continue
        d, k, l, n, th, c, h = vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6]
        neck = vals[7]
        s_min, h1, r = vals[-3], vals[-2], vals[-1]
        rows.append([pn, str(dn), m.group(2), m.group(3), d, k, l, n, th,
                     c, neck, neck, s_min, h1, r, h])
    return rows


def parse_one(text, pn):
    rows = []
    for line in text.splitlines():
        m = ONE.match(line.strip())
        if not m:
            continue
        dn = int(m.group(1))
        if dn > 600:
            continue
        vals = _num_tokens(m.group(3))
        if len(vals) < 11:
            continue
        d, k, l, n, th, c, h = vals[0], vals[1], vals[2], vals[3], vals[4], vals[5], vals[6]
        neck = vals[7]
        s_min, h1, r = vals[-3], vals[-2], vals[-1]
        rows.append([pn, str(dn), m.group(2), m.group(2), d, k, l, n, th,
                     c, neck, neck, s_min, h1, r, h])
    return rows


def main():
    with pdfplumber.open(PDF) as pdf:
        p44 = pdf.pages[43].extract_text() or ''
        p45 = pdf.pages[44].extract_text() or ''
        p54 = pdf.pages[53].extract_text() or ''
        p55 = pdf.pages[54].extract_text() or ''

    p44 = p44[p44.find('表27'):]
    rows = parse_two(p44, '2.5') + parse_two(p45, '2.5')
    i54 = p54.find('表37')
    rows += parse_one(p54[:i54], '250')
    rows += parse_one(p54[i54:], '320')
    rows += parse_one(p55[p55.find('表38'):], '400')

    with open(OUT, encoding='utf-8-sig', newline='') as fh:
        old = list(csv.DictReader(fh))
    merged = {}
    for r in old:
        merged[(r['PN'], r['DN'])] = [r[h] for h in HEAD]
    for r in rows:
        merged[(r[0], r[1])] = r
    out = [merged[k] for k in sorted(merged,
                                     key=lambda x: (float(x[0]), int(x[1])))]
    with open(OUT, 'w', encoding='utf-8', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow(HEAD)
        writer.writerows(out)
    print('total', len(out))
    for pn in ('2.5', '250', '320', '400'):
        print(pn, sum(1 for r in out if r[0] == pn))


if __name__ == '__main__':
    main()
