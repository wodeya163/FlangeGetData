# -*- coding: utf-8 -*-
"""按 PDF 已核对行做关键规格抽查。"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import main  # noqa: E402

CASES = [
    ('GBT9124_2_带颈对焊.csv', '900', '600',
     {'D': '1040', 'K': '901.7', 'C': '139.7', 'H': '292', 'N_A': '749'}),
    ('GBT9124_2_带颈平焊.csv', '600', '600',
     {'D': '940', 'K': '838.2', 'C': '101.6', 'H': '140', 'N_A': '718'}),
    ('GBT9124_2_整体.csv', '300', '50',
     {'D': '165', 'K': '127.0', 'C': '20.7', 'N_A': '84'}),
    ('GBT9124_2_承插焊.csv', '1500', '50',
     {'D': '215', 'K': '165.1', 'C': '38.1', 'H': '57', 'N_A': '105'}),
    ('GBT9124_2_螺纹.csv', '2500', '50',
     {'D': '235', 'K': '171.4', 'C': '50.9', 'H': '70', 'N_A': '95'}),
    ('GBT9124_2_法兰盖.csv', '150', '50',
     {'D': '150', 'K': '120.7', 'C': '17.5'}),
]
fail = 0
for name, cls, dn, expect in CASES:
    _h, rows = main.load_csv(os.path.join(ROOT, 'Data', name))
    row = next((r for r in rows if r['Class'] == cls and r['DN'] == dn), None)
    if row is None:
        print('MISS', name, cls, dn)
        fail += 1
        continue
    bad = [(k, v, row.get(k)) for k, v in expect.items() if row.get(k) != v]
    print(('FAIL' if bad else 'PASS'), name, cls, dn, bad)
    fail += bool(bad)
print('failures', fail)
