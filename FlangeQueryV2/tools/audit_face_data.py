# -*- coding: utf-8 -*-
"""审计法兰面型尺寸缺口：输出 JSON + Markdown 清单。"""

import csv
import datetime
import glob
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'Data')
DOC = os.path.join(ROOT, 'docs', '数据缺口清单.md')
OUT = os.path.join(DATA, 'face_audit.json')
FLANGE_PREFIX = ('GBT9124_1_', 'GBT9124_2_', 'HGT20592_', 'HGT20615_',
                 'HGT20623_', 'NBT47023')


def main():
    items = []
    files = 0
    total = 0
    for path in sorted(glob.glob(os.path.join(DATA, '*.csv'))):
        name = os.path.basename(path)
        if not name.startswith(FLANGE_PREFIX):
            continue
        with io.open(path, encoding='utf-8-sig', newline='') as fh:
            rd = csv.DictReader(fh)
            fields = rd.fieldnames or []
            if not all(c in fields for c in ('D', 'K', 'C')):
                continue
            rows = list(rd)
        files += 1
        for row in rows:
            total += 1
            if str(row.get('RF_d', '')).strip() and \
                    str(row.get('RF_f1', '')).strip():
                continue
            items.append({
                'file': name,
                'DN': row.get('DN', ''),
                'PN': row.get('PN', ''),
                'Class': row.get('Class', ''),
                'face': row.get('密封面', ''),
            })
    payload = {
        'generated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'flange_files': files,
        'total_rows': total,
        'rf_missing': len(items),
        'items': items,
    }
    with io.open(OUT, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)

    groups = {}
    for it in items:
        groups[it['file']] = groups.get(it['file'], 0) + 1
    lines = [
        '# 法兰面型尺寸缺口清单',
        '',
        '> 生成时间：%s' % payload['generated'],
        '> 范围：%d 个法兰表，%d 行；RF_d/RF_f1 缺失 %d 行。'
        % (files, total, len(items)),
        '',
        '缺尺寸的行在程序中标“近似”，不冒充标准值。',
        '',
        '## 按文件汇总',
        '',
        '| 文件 | 缺失行数 |',
        '|---|---:|',
    ]
    for name, count in sorted(groups.items()):
        lines.append('| %s | %d |' % (name, count))
    lines += ['', '## 明细（前 80 行）', '',
              '| 文件 | DN | PN | Class | 面型 |',
              '|---|---|---|---|---|']
    for it in items[:80]:
        lines.append('| %s | %s | %s | %s | %s |' % (
            it['file'], it['DN'], it['PN'], it['Class'], it['face']))
    if len(items) > 80:
        lines.append('| … | 其余 %d 行见 `Data/face_audit.json` | | | |'
                     % (len(items) - 80))
    with io.open(DOC, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(lines) + '\n')
    print('法兰表：%d，总行：%d，RF 缺失：%d' % (files, total, len(items)))
    print('清单：', DOC)
    print('JSON：', OUT)


if __name__ == '__main__':
    main()
