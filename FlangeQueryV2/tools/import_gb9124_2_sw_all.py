# -*- coding: utf-8 -*-
"""GB/T 9124.2 SW 承插焊 Class150–1500。

SW 与 SO 同 Class/DN 的 C/H/N 相同；SW 仅小口径：
Class300/600 ≤DN80，Class900/1500 ≤DN65。Class2500 待补。
"""

import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import main as app  # noqa: E402

HEAD = ['Class', 'DN', 'DN2', 'A1_A', 'D', 'K', 'L', 'n', 'Th',
        'C', 'H', 'N_A']


def main():
    _h, base = app.load_csv(os.path.join(
        ROOT, 'Data', 'GBT9124_2_承插焊_Class150.csv'))
    _h, so = app.load_csv(os.path.join(
        ROOT, 'Data', 'GBT9124_2_带颈平焊.csv'))
    rows = [[r['Class'], r['DN'], r['DN2'], r['A1_A'], r['D'], r['K'],
             r['L'], r['n'], r['Th'], r['C'], r['H'], r['N_A']]
            for r in base]
    limits = {'300': 80, '600': 80, '900': 65, '1500': 65}
    for cls, limit in limits.items():
        for r in so:
            if r['Class'] == cls and int(r['DN']) <= limit:
                rows.append([cls, r['DN'], r['DN2'], r['A1_A'], r['D'],
                             r['K'], r['L'], r['n'], r['Th'], r['C'],
                             r['H'], r['N_A']])
    with open(os.path.join(ROOT, 'Data', 'GBT9124_2_承插焊.csv'),
              'w', encoding='utf-8', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow(HEAD)
        writer.writerows(rows)
    print('rows', len(rows))


if __name__ == '__main__':
    main()
