# -*- coding: utf-8 -*-
"""跨类型数据一致性校验：D/K/L/n/Th 应一致；C/H/N 按共享规则检查。"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import main  # noqa: E402

FILES = {
    'WN': 'GBT9124_2_带颈对焊.csv',
    'SO': 'GBT9124_2_带颈平焊.csv',
    'IF': 'GBT9124_2_整体.csv',
    'SW': 'GBT9124_2_承插焊.csv',
    'TH': 'GBT9124_2_螺纹.csv',
    'BL': 'GBT9124_2_法兰盖.csv',
}
DATA = {}
for key, name in FILES.items():
    _h, rows = main.load_csv(os.path.join(ROOT, 'Data', name))
    DATA[key] = {(r['Class'], r['DN']): r for r in rows}
    print(key, len(rows))

base = DATA['WN']
issues = []
for key in ('SO', 'IF', 'SW', 'TH', 'BL'):
    for (cls, dn), row in DATA[key].items():
        ref = base.get((cls, dn))
        if not ref:
            issues.append('%s %s/%s 在 WN 中无对应行' % (key, cls, dn))
            continue
        for col in ('D', 'K', 'L', 'n', 'Th'):
            if row.get(col) != ref.get(col):
                issues.append('%s %s/%s %s: %s != WN %s'
                              % (key, cls, dn, col, row.get(col), ref.get(col)))
        if key in ('SO', 'IF') and cls != '150':
            for col in ('C', 'N_A'):
                if row.get(col) != ref.get(col):
                    issues.append('%s %s/%s %s: %s != WN %s'
                                  % (key, cls, dn, col, row.get(col), ref.get(col)))
        if key in ('SW', 'TH') and row.get('H') != DATA['SO'].get((cls, dn), {}).get('H'):
            issues.append('%s %s/%s H: %s != SO %s'
                          % (key, cls, dn, row.get('H'),
                             DATA['SO'].get((cls, dn), {}).get('H')))
        if key == 'BL' and row.get('C') != DATA['SO'].get((cls, dn), {}).get('C'):
            issues.append('BL %s/%s C: %s != SO %s'
                          % (cls, dn, row.get('C'),
                             DATA['SO'].get((cls, dn), {}).get('C')))

print('\nissues:', len(issues))
for i in issues[:60]:
    print(i)
