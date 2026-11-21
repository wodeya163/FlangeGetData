# -*- coding: utf-8 -*-
"""FIX-19：SQLite + manifest 构建测试。"""

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

try:
    from tools.build_data import build, load_sqlite
except ImportError as exc:
    raise unittest.SkipTest('构建依赖不可用，跳过数据构建测试：%s' % exc)


class DataBuildTest(unittest.TestCase):
    def test_build_manifest_and_sqlite(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, 'data.db')
            manifest_path = os.path.join(tmp, 'manifest.json')
            manifest = build(db, manifest_path)
            self.assertEqual(len(manifest['files']), 58)
            self.assertTrue(os.path.isfile(db))
            self.assertTrue(os.path.isfile(manifest_path))

            head, rows = load_sqlite('HGT20592_带颈对焊.csv', db)
            self.assertEqual(len(rows), 146)
            self.assertEqual(rows[0]['PN'], '10')
            self.assertEqual(rows[0]['DN'], '10')

            head, _rows = load_sqlite('HGT20615_带颈对焊.csv', db)
            self.assertIn('Class', head)
            self.assertNotIn('PN', head)


if __name__ == '__main__':
    unittest.main()
