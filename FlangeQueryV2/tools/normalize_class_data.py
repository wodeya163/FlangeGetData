# -*- coding: utf-8 -*-
"""FIX-11：清理 Class 体系 CSV 的伪 PN 列。

背景：HGT20615_* / HGT20623_* 的 PN 列被写成 class_150 之类的伪值，
HGT20615_法兰盖 还把 Class 写成了 PN2。本脚本：

1. 若存在 PN2 且无 Class，则把 PN2 改名为 Class；
2. 删除 PN 列（删除前确认该列全部为空或 class_* 伪值）；
3. 原地重写文件，保留原编码/BOM 与换行风格；
4. --apply 时先备份到 _archive/data_before_fix11/。

默认 dry-run，只打印将要修改的内容。
"""

import argparse
import csv
import io
import os
import shutil
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'Data')
ARCHIVE = os.path.join(os.path.dirname(ROOT), '_archive', 'data_before_fix11')


def class_files():
    return sorted(
        n for n in os.listdir(DATA)
        if n.lower().endswith('.csv')
        and (n.startswith('HGT20615_') or n.startswith('HGT20623_'))
    )


def read_table(path):
    with open(path, 'rb') as fh:
        raw = fh.read()
    bom = raw.startswith(b'\xef\xbb\xbf')
    text = raw.decode('utf-8-sig' if bom else 'utf-8')
    crlf = '\r\n' in text
    rows = list(csv.reader(io.StringIO(text)))
    return rows, bom, crlf


def write_table(path, rows, bom, crlf):
    with open(path, 'w', encoding='utf-8-sig' if bom else 'utf-8',
              newline='') as fh:
        writer = csv.writer(fh, lineterminator='\r\n' if crlf else '\n')
        writer.writerows(rows)


def plan(path):
    rows, bom, crlf = read_table(path)
    head = rows[0]
    actions = []
    if 'PN2' in head and 'Class' not in head:
        head[head.index('PN2')] = 'Class'
        actions.append('PN2->Class')
    if 'PN' in head:
        idx = head.index('PN')
        bad = [r[idx] for r in rows[1:]
               if len(r) > idx and r[idx].strip()
               and not r[idx].strip().lower().startswith('class')]
        if bad:
            raise SystemExit('%s 的 PN 列含非伪值，停止：%s'
                             % (os.path.basename(path), bad[:5]))
        del head[idx]
        for r in rows[1:]:
            if len(r) > idx:
                del r[idx]
        actions.append('drop PN')
    return rows, bom, crlf, actions


def main():
    parser = argparse.ArgumentParser(description='清理 Class 体系 CSV 的伪 PN')
    parser.add_argument('--apply', action='store_true', help='实际写入并备份')
    args = parser.parse_args()

    files = class_files()
    print('Class 体系 CSV：%d 个' % len(files))
    changed = 0
    for name in files:
        path = os.path.join(DATA, name)
        rows, bom, crlf, actions = plan(path)
        if not actions:
            print('  跳过（已干净）：%s' % name)
            continue
        changed += 1
        print('  %s: %s（%d 行）' % (name, ', '.join(actions), len(rows) - 1))
        if args.apply:
            os.makedirs(ARCHIVE, exist_ok=True)
            backup = os.path.join(ARCHIVE, name)
            if not os.path.exists(backup):
                shutil.copy2(path, backup)
            write_table(path, rows, bom, crlf)
    print('待修改/已修改：%d 个' % changed)
    if not args.apply:
        print('dry-run，未写入。确认后加 --apply。')


if __name__ == '__main__':
    main()
