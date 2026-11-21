# -*- coding: utf-8 -*-
"""给 GB/T 9124.2 CSV 增加 S（钢管壁厚）与 d（内径）。

标准表不提供壁厚，这里用 ASME B36.10M Sch40 作为默认系列：
S = Sch40 壁厚，d = 钢管外径 - 2S。
可用 --schedule 改成 STD/Sch80 等。
"""

import argparse
import csv
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, 'Data')
PIPE = os.path.join(DATA, 'ANSIB36.10M_B36.19M.csv')
FILES = [
    'GBT9124_2_带颈对焊.csv',
    'GBT9124_2_带颈平焊.csv',
    'GBT9124_2_整体.csv',
    'GBT9124_2_承插焊.csv',
    'GBT9124_2_螺纹.csv',
    'GBT9124_2_法兰盖.csv',
]


def num(text):
    try:
        return float(str(text).strip())
    except (TypeError, ValueError):
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--schedule', default='Sch40')
    args = parser.parse_args()
    with open(PIPE, encoding='utf-8-sig', newline='') as fh:
        pipe_rows = list(csv.DictReader(fh))
    by_dn, by_dn2 = {}, {}
    for row in pipe_rows:
        if row.get('DN'):
            by_dn[row['DN'].strip()] = row
        if row.get('DN2'):
            by_dn2[row['DN2'].strip().lower()] = row
    for name in FILES:
        path = os.path.join(DATA, name)
        with open(path, encoding='utf-8-sig', newline='') as fh:
            rows = list(csv.DictReader(fh))
            fields = list(rows[0].keys()) if rows else []
        fields = [f for f in fields if f != 'd']
        for col in ('S', 'd_bore'):
            if col not in fields:
                fields.append(col)
        for row in rows:
            row.pop('d', None)
            p = by_dn2.get(str(row.get('DN2', '')).strip().lower())
            if p is None:
                p = by_dn.get(str(row.get('DN', '')).strip())
            s = num(p.get(args.schedule)) if p else None
            row['S'] = '' if s is None else '%.2f' % s
            a1 = num(row.get('A1_A')) or num(p.get('D_o') if p else None)
            if name.endswith('法兰盖.csv') or s is None or a1 is None:
                row['d_bore'] = ''
            else:
                row['d_bore'] = '%.2f' % max(1.0, a1 - 2 * s)
        with open(path, 'w', encoding='utf-8-sig', newline='') as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        print(name, len(rows), 'schedule', args.schedule)


if __name__ == '__main__':
    main()
