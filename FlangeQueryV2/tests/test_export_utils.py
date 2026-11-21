# -*- coding: utf-8 -*-
import csv
import os
import tempfile
import unittest

from flange_export import resolve_export_columns, write_csv


class ExportColumnsTest(unittest.TestCase):
    def test_visible_columns_keep_page_specific_fields(self):
        rows = [{
            '序号': '1', 'DN': '50', '接管规格': 'φ60×3.5', 'D_o': '60',
            'h': '8', 'q': '8', 'r': '1.85', 'Lt': '15', 'N': '20', 'a': '20.56',
        }]
        visible = ['序号', 'DN', '接管规格', 'D_o', 'h', 'q', 'r', 'Lt', 'N', 'a']
        cols = resolve_export_columns(rows, visible, ['DN'])
        self.assertEqual(cols, visible)

    def test_visible_columns_handle_pipe_wall_thickness(self):
        rows = [{'DN': '150', 'D_o': '168.3', 'Sch40': '7.11', 'Sch80': '10.97'}]
        cols = resolve_export_columns(rows, ['DN', 'D_o', 'Sch40', 'Sch80'],
                                      ['DN', 'D'])
        self.assertEqual(cols, ['DN', 'D_o', 'Sch40', 'Sch80'])

    def test_fallback_when_visible_columns_are_unavailable(self):
        rows = [{'DN': '100', 'D': '220', 'K': '180'}]
        cols = resolve_export_columns(rows, [], ['DN', 'D', 'K', 'H'])
        self.assertEqual(cols, ['DN', 'D', 'K'])

    def test_empty_rows_return_no_columns(self):
        self.assertEqual(resolve_export_columns([], ['DN'], ['DN']), [])

    def test_duplicate_columns_are_removed(self):
        rows = [{'DN': '100', 'D': '220'}]
        cols = resolve_export_columns(rows, ['DN', 'D', 'DN'], ['D'])
        self.assertEqual(cols, ['DN', 'D'])


class WriteCsvTest(unittest.TestCase):
    def test_write_csv_uses_utf8_sig_and_keeps_values(self):
        rows = [{'DN': '50', '接管规格': 'φ60×3.5', 'h': '8'}]
        cols = ['DN', '接管规格', 'h']
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'out.csv')
            write_csv(path, rows, cols)
            with open(path, 'rb') as f:
                self.assertTrue(f.read(3) == b'\xef\xbb\xbf')
            with open(path, encoding='utf-8-sig', newline='') as f:
                data = list(csv.reader(f))
        self.assertEqual(data, [cols, ['50', 'φ60×3.5', '8']])


if __name__ == '__main__':
    unittest.main()
