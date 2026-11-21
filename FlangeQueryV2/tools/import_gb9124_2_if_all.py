# -*- coding: utf-8 -*-
"""GB/T 9124.2 IF 整体法兰 Class150–2500。

Class150 来自表7（C 与 WN 不同）；Class300–2500 按表8–12，
C/N 与同 Class 的 WN 相同，去除 WN 的 H/A 列。
"""

import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import main as app  # noqa: E402

HEAD = ['Class', 'DN', 'DN2', 'D', 'K', 'L', 'n', 'Th', 'C', 'N_A']


def main():
    _h, base = app.load_csv(os.path.join(
        ROOT, 'Data', 'GBT9124_2_整体_Class150.csv'))
    _h, wn = app.load_csv(os.path.join(
        ROOT, 'Data', 'GBT9124_2_带颈对焊.csv'))
    rows = [[r['Class'], r['DN'], r['DN2'], r['D'], r['K'], r['L'],
             r['n'], r['Th'], r['C'], r['N_A']] for r in base]
    for cls in ('300', '600', '900', '1500', '2500'):
        for r in wn:
            if r['Class'] != cls:
                continue
            rows.append([cls, r['DN'], r['DN2'], r['D'], r['K'], r['L'],
                         r['n'], r['Th'], r['C'], r['N_A']])
    with open(os.path.join(ROOT, 'Data', 'GBT9124_2_整体.csv'),
              'w', encoding='utf-8', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow(HEAD)
        writer.writerows(rows)
    print('rows', len(rows))


if __name__ == '__main__':
    main()
