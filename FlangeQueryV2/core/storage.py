# -*- coding: utf-8 -*-
"""SQLite 运行时读取：优先 data.db，缺失时回退 CSV。"""

import json
import os
import re
import sqlite3

_IDENT = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def has_database(db_path):
    return bool(db_path) and os.path.isfile(db_path)


def load_sqlite(csv_name, db_path):
    """按 CSV 文件名从 manifest 读取 (head, rows)。"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        meta = conn.execute(
            'SELECT table_name, columns FROM manifest WHERE file=?',
            (csv_name,)).fetchone()
        if meta is None:
            raise KeyError('manifest 中没有：%s' % csv_name)
        table = meta['table_name']
        if not _IDENT.match(table):
            raise ValueError('非法表名：%s' % table)
        head = json.loads(meta['columns'])
        rows = []
        for row in conn.execute('SELECT * FROM %s ORDER BY _row' % table):
            rows.append({head[i]: row['c%d' % i] for i in range(len(head))})
        return head, rows
    finally:
        conn.close()


def load_page(csv_name, csv_loader, csv_path=None, db_path=None,
              prefer_db=True):
    """优先 SQLite；失败/缺失时回退 `csv_loader(csv_path)`。"""
    if prefer_db and has_database(db_path):
        try:
            return load_sqlite(csv_name, db_path)
        except (KeyError, ValueError, sqlite3.Error, OSError):
            pass
    if csv_path is None:
        raise FileNotFoundError(csv_name)
    return csv_loader(csv_path)
