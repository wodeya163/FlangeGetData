# -*- coding: utf-8 -*-
"""SQLite 与 CSV 全量一致性测试。"""

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import main  # noqa: E402
from core import storage  # noqa: E402
from tools import build_data  # noqa: E402


class SqliteParityTest(unittest.TestCase):
    def test_all_csv_files_match_sqlite(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, 'data.db')
            manifest = os.path.join(tmp, 'manifest.json')
            build_data.build(db, manifest)
            names = sorted(n for n in os.listdir(os.path.join(ROOT, 'Data'))
                           if n.lower().endswith('.csv'))
            self.assertGreaterEqual(len(names), 50)
            for name in names:
                with self.subTest(csv=name):
                    csv_head, csv_rows = main.load_csv(
                        os.path.join(ROOT, 'Data', name))
                    db_head, db_rows = storage.load_sqlite(name, db)
                    self.assertEqual(db_head, csv_head)
                    self.assertEqual(len(db_rows), len(csv_rows))
                    if csv_rows:
                        self.assertEqual(db_rows[0], csv_rows[0])

    def test_source_helper_reports_sqlite(self):
        db = os.path.join(ROOT, 'Data', 'data.db')
        if not storage.has_database(db):
            self.skipTest('Data/data.db 不存在')
        old = main.DB_PATH
        try:
            main.DB_PATH = db
            main.SQLITE_ENABLED = True
            _h, rows, source = main.load_page_with_source(
                'GBT9124_2_带颈对焊.csv',
                os.path.join(ROOT, 'Data', 'GBT9124_2_带颈对焊.csv'))
            self.assertEqual(source, 'SQLite')
            self.assertEqual(len(rows), 112)
        finally:
            main.DB_PATH = old


if __name__ == '__main__':
    unittest.main()
