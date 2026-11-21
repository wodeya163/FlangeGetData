# -*- coding: utf-8 -*-
"""FIX-02：加载行数契约测试。

背景：2026-10-22 修复了 load_csv 的 off-by-one —— 首列为空表头的 CSV
（HG/T 20592 等）会把第一条数据（PN10/DN10）丢掉。本测试锁定两条契约：

1. 每个 CSV 的加载行数 == 原始数据行数（空行除外）；
2. 带行号列的 CSV 首条数据必须保留，行号列不进入表头。

需要 PyQt5（main.py 顶部导入），无 PyQt5 环境自动跳过。
"""

import csv
import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

try:
    import main
except ImportError as exc:  # 无 PyQt5 的环境跳过，不阻塞纯逻辑测试
    raise unittest.SkipTest('PyQt5 不可用，跳过加载契约测试：%s' % exc)

DATA_DIR = os.path.join(ROOT, 'Data')


def _read_raw_rows(path):
    """按 load_csv 相同的编码顺序读取原始行，过滤空行。"""
    for enc in ('utf-8-sig', 'gbk', 'latin1'):
        try:
            with open(path, encoding=enc, newline='') as fh:
                return [r for r in csv.reader(fh) if r]
        except UnicodeDecodeError:
            continue
    raise AssertionError('无法解码: %s' % path)


class LoadCsvContractTest(unittest.TestCase):
    def test_every_csv_loads_all_data_rows(self):
        """逐文件校验：不允许丢首行，也不允许静默丢行。"""
        names = sorted(n for n in os.listdir(DATA_DIR)
                       if n.lower().endswith('.csv'))
        self.assertTrue(names, 'Data 目录没有 CSV')
        for name in names:
            with self.subTest(csv=name):
                path = os.path.join(DATA_DIR, name)
                raw = _read_raw_rows(path)
                head, rows = main.load_csv(path)
                self.assertTrue(head, '表头为空: %s' % name)
                self.assertEqual(
                    len(rows), len(raw) - 1,
                    '加载行数 %d != 原始数据行数 %d: %s'
                    % (len(rows), len(raw) - 1, name))
                self.assertTrue(rows, '没有数据行: %s' % name)
                self.assertEqual(set(rows[0].keys()), set(head),
                                 '行字典键与表头不一致: %s' % name)

    def test_index_column_keeps_first_data_row(self):
        """回归点：HG/T 20592 WN 的 PN10/DN10 曾因二次切片丢失。"""
        path = os.path.join(DATA_DIR, 'HGT20592_带颈对焊.csv')
        raw = _read_raw_rows(path)
        head, rows = main.load_csv(path)
        self.assertEqual(len(rows), len(raw) - 1)
        self.assertEqual((rows[0]['PN'], rows[0]['DN']), ('10', '10'))
        self.assertNotIn('', head, '空行号列不应进入表头')

    def test_no_index_column_file_keeps_first_data_row(self):
        """无行号列的 CSV 同样不能把表头当数据、或丢首行。"""
        path = os.path.join(DATA_DIR, 'HGT20606_RF.csv')
        raw = _read_raw_rows(path)
        head, rows = main.load_csv(path)
        self.assertEqual(len(rows), len(raw) - 1)
        self.assertEqual(rows[0]['标准'], 'HG/T 20606')
        self.assertEqual(rows[0]['DN'], '10')

    def test_malformed_row_is_skipped_not_counted(self):
        """列数不符的行应跳过，且不影响后续正常行。"""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'bad.csv')
            with open(path, 'w', encoding='utf-8', newline='') as fh:
                fh.write('DN,PN\n10,16\n20,16,extra\n25,16\n')
            head, rows = main.load_csv(path)
        self.assertEqual(head, ['DN', 'PN'])
        self.assertEqual([r['DN'] for r in rows], ['10', '25'])


if __name__ == '__main__':
    unittest.main()
