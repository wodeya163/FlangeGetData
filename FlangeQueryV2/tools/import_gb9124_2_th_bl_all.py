# -*- coding: utf-8 -*-
"""由 SO Class150–1500 生成 Th（表13–18）与 BL（表40–45）数据。

Th 与 SO 的 C/H/N 相同；BL 仅保留法兰盖厚度 C。
Class2500 的 Th/BL 表尚未录入。
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
    _h, so = app.load_csv(os.path.join(
        ROOT, 'Data', 'GBT9124_2_带颈平焊.csv'))
    th = [[r['Class'], r['DN'], r['DN2'], r['A1_A'], r['D'], r['K'],
           r['L'], r['n'], r['Th'], r['C'], r['H'], r['N_A']] for r in so]
    bl = [[r['Class'], r['DN'], r['DN2'], r['D'], r['K'], r['L'],
           r['n'], r['Th'], r['C']] for r in so]
    with open(os.path.join(ROOT, 'Data', 'GBT9124_2_螺纹.csv'),
              'w', encoding='utf-8', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow(HEAD)
        writer.writerows(th)
    with open(os.path.join(ROOT, 'Data', 'GBT9124_2_法兰盖.csv'),
              'w', encoding='utf-8', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow(['Class', 'DN', 'DN2', 'D', 'K', 'L', 'n',
                         'Th', 'C'])
        writer.writerows(bl)
    print('th', len(th), 'bl', len(bl))


if __name__ == '__main__':
    main()
