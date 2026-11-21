# -*- coding: utf-8 -*-
"""SQLite 运行时与 CSV 回退测试。"""

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core import storage  # noqa: E402
import main  # noqa: E402


class StorageTest(unittest.TestCase):
    def test_csv_fallback_without_db(self):
        path = os.path.join(ROOT, 'Data', 'GBT9124_2_带颈对焊.csv')
        head, rows = storage.load_page(
            'GBT9124_2_带颈对焊.csv', main.load_csv, path,
            db_path=os.path.join(tempfile.gettempdir(), 'no-such.db'))
        self.assertTrue(head)
        self.assertEqual(len(rows), 112)

    def test_sqlite_roundtrip_if_available(self):
        db = os.path.join(ROOT, 'Data', 'data.db')
        if not storage.has_database(db):
            self.skipTest('Data/data.db 不存在')
        head, rows = storage.load_sqlite('GBT9124_2_带颈对焊.csv', db)
        self.assertIn('DN', head)
        self.assertEqual(len(rows), 112)
        self.assertEqual(rows[0]['Class'], '150')


if __name__ == '__main__':
    unittest.main()
