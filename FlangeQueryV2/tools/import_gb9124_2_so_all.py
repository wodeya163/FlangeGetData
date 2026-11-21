# -*- coding: utf-8 -*-
"""合并 GB/T 9124.2 SO Class150–1500。

Class150 来自表25；Class300/600/900/1500 的 D/K/L/C/N 与 WN 相同，
按表26–29 覆盖法兰高度 H。Class1500 SO 仅 DN15–65；Class2500 SO 标准未列。
"""

import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import main as app  # noqa: E402

HEAD = ['Class', 'DN', 'DN2', 'A1_A', 'D', 'K', 'L', 'n', 'Th',
        'C', 'H', 'N_A']
H_MAP = {
    '300': {'15': '21', '20': '24', '25': '25', '32': '25', '40': '29',
            '50': '32', '65': '37', '80': '41', '100': '46', '125': '49',
            '150': '51', '200': '60', '250': '65', '300': '71',
            '350': '75', '400': '81', '450': '87', '500': '94',
            '550': '100', '600': '105'},
    '600': {'15': '22', '20': '25', '25': '27', '32': '29', '40': '32',
            '50': '37', '65': '41', '80': '46', '100': '54', '125': '60',
            '150': '67', '200': '76', '250': '86', '300': '92',
            '350': '94', '400': '106', '450': '117', '500': '127',
            '550': '133', '600': '140'},
    '900': {'15': '32', '20': '35', '25': '41', '32': '41', '40': '44',
            '50': '57', '65': '64', '80': '54', '100': '70', '125': '79',
            '150': '86', '200': '102', '250': '108', '300': '117',
            '350': '130', '400': '133', '450': '152', '500': '159',
            '600': '203'},
    '1500': {'15': '32', '20': '35', '25': '41', '32': '41', '40': '44',
             '50': '57', '65': '64'},
}


def main():
    _h, base = app.load_csv(os.path.join(
        ROOT, 'Data', 'GBT9124_2_带颈平焊_Class150.csv'))
    _h, wn = app.load_csv(os.path.join(
        ROOT, 'Data', 'GBT9124_2_带颈对焊.csv'))
    rows = [[r['Class'], r['DN'], r['DN2'], r['A1_A'], r['D'], r['K'],
             r['L'], r['n'], r['Th'], r['C'], r['H'], r['N_A']]
            for r in base]
    for cls in ('300', '600', '900', '1500'):
        for r in wn:
            if r['Class'] != cls or r['DN'] not in H_MAP[cls]:
                continue
            rows.append([cls, r['DN'], r['DN2'], r['A1_A'], r['D'], r['K'],
                         r['L'], r['n'], r['Th'], r['C'],
                         H_MAP[cls][r['DN']], r['N_A']])
    with open(os.path.join(ROOT, 'Data', 'GBT9124_2_带颈平焊.csv'),
              'w', encoding='utf-8', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow(HEAD)
        writer.writerows(rows)
    print('rows', len(rows))


if __name__ == '__main__':
    main()
