# -*- coding: utf-8 -*-
"""补齐 GB/T 9124.2 Th/BL Class2500（表18/45）。

C/N 取同 Class 的 WN；Th 的 H 按表18：40/43/48/52/60/70/79。
"""

import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import main as app  # noqa: E402

HEAD = ['Class', 'DN', 'DN2', 'A1_A', 'D', 'K', 'L', 'n', 'Th',
        'C', 'H', 'N_A']
H = {'15': '40', '20': '43', '25': '48', '32': '52', '40': '60',
     '50': '70', '65': '79'}


def main():
    _h, wn = app.load_csv(os.path.join(ROOT, 'Data', 'GBT9124_2_带颈对焊.csv'))
    _h, th = app.load_csv(os.path.join(ROOT, 'Data', 'GBT9124_2_螺纹.csv'))
    _h, bl = app.load_csv(os.path.join(ROOT, 'Data', 'GBT9124_2_法兰盖.csv'))
    th_rows = [[r['Class'], r['DN'], r['DN2'], r['A1_A'], r['D'], r['K'],
                r['L'], r['n'], r['Th'], r['C'], r['H'], r['N_A']] for r in th]
    bl_rows = [[r['Class'], r['DN'], r['DN2'], r['D'], r['K'], r['L'],
                r['n'], r['Th'], r['C']] for r in bl]
    for r in wn:
        if r['Class'] == '2500' and r['DN'] in H:
            th_rows.append(['2500', r['DN'], r['DN2'], '', r['D'], r['K'],
                            r['L'], r['n'], r['Th'], r['C'], H[r['DN']],
                            r['N_A']])
            bl_rows.append(['2500', r['DN'], r['DN2'], r['D'], r['K'],
                            r['L'], r['n'], r['Th'], r['C']])
    with open(os.path.join(ROOT, 'Data', 'GBT9124_2_螺纹.csv'),
              'w', encoding='utf-8', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow(HEAD)
        writer.writerows(th_rows)
    with open(os.path.join(ROOT, 'Data', 'GBT9124_2_法兰盖.csv'),
              'w', encoding='utf-8', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow(['Class', 'DN', 'DN2', 'D', 'K', 'L', 'n',
                         'Th', 'C'])
        writer.writerows(bl_rows)
    print('th', len(th_rows), 'bl', len(bl_rows))


if __name__ == '__main__':
    main()
