# -*- coding: utf-8 -*-
"""FIX-19：从归一化 CSV 构建 SQLite 数据库与 manifest.json。

产物：
- Data/data.db       每个 CSV 一张表（t_000...），外加 manifest 元数据表
- Data/manifest.json 文件、行数、列、SHA256、版本与生成时间

CSV 仍是编辑源；SQLite 用于后续按尺寸索引查询与数据包校验。
"""

import datetime
import hashlib
import json
import os
import sqlite3
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import main  # noqa: E402  (需要 PyQt5，与运行时相同的归一化逻辑)

DATA = os.path.join(ROOT, 'Data')
DEFAULT_DB = os.path.join(DATA, 'data.db')
DEFAULT_MANIFEST = os.path.join(DATA, 'manifest.json')


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _quote(name):
    return '"%s"' % str(name).replace('"', '""')


def _version():
    ns = {}
    with open(os.path.join(ROOT, 'version.py'), encoding='utf-8') as fh:
        exec(compile(fh.read(), 'version.py', 'exec'), ns)
    return ns['APP_VERSION']


def build(db_path=DEFAULT_DB, manifest_path=DEFAULT_MANIFEST):
    names = sorted(n for n in os.listdir(DATA) if n.lower().endswith('.csv'))
    if not names:
        raise SystemExit('Data 目录没有 CSV')
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute('CREATE TABLE manifest (file TEXT PRIMARY KEY, table_name TEXT,'
                     ' rows INTEGER, sha256 TEXT, columns TEXT, review TEXT)')
        files = []
        for index, name in enumerate(names):
            path = os.path.join(DATA, name)
            head, rows = main.load_csv(path)
            table = 't_%03d' % index
            # SQLite 标识符大小写不敏感（D 与 d 会冲突），物理列统一用 c0..cN，
            # 原始列名保存在 manifest 的 columns 里。
            columns = ', '.join(['_row INTEGER'] +
                                ['c%d TEXT' % i for i in range(len(head))])
            conn.execute('CREATE TABLE %s (%s)' % (_quote(table), columns))
            placeholders = ', '.join(['?'] * (len(head) + 1))
            conn.executemany(
                'INSERT INTO %s VALUES (%s)' % (_quote(table), placeholders),
                [[i] + [str(row.get(col, '')) for col in head]
                 for i, row in enumerate(rows)])
            digest = _sha256(path)
            review = main.review_for(name)
            conn.execute('INSERT INTO manifest VALUES (?,?,?,?,?,?)',
                         (name, table, len(rows), digest,
                          json.dumps(head, ensure_ascii=False),
                          json.dumps(review, ensure_ascii=False)))
            files.append({'file': name, 'table': table, 'rows': len(rows),
                          'sha256': digest, 'columns': head,
                          'review': review})
        conn.commit()
    finally:
        conn.close()

    manifest = {
        'version': _version(),
        'generated': datetime.datetime.now().isoformat(timespec='seconds'),
        'files': files,
    }
    with open(manifest_path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    print('SQLite：%s（%d 张表）' % (db_path, len(files)))
    print('清单：%s' % manifest_path)
    return manifest


def load_sqlite(csv_name, db_path=DEFAULT_DB):
    """按 CSV 文件名从 SQLite 读回 (head, rows)，用于测试与后续运行时。"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    meta = conn.execute(
        'SELECT table_name, columns FROM manifest WHERE file=?',
        (csv_name,)).fetchone()
    if meta is None:
        conn.close()
        raise KeyError('manifest 中没有：%s' % csv_name)
    head = json.loads(meta['columns'])
    rows = []
    for row in conn.execute('SELECT * FROM %s ORDER BY _row'
                            % _quote(meta['table_name'])):
        rows.append({head[i]: row['c%d' % i] for i in range(len(head))})
    conn.close()
    return head, rows


if __name__ == '__main__':
    build()
