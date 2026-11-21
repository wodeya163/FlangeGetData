# -*- coding: utf-8 -*-
"""FIX-14：TSV 与 XLSX 导出格式的单元测试。"""

import os
import sys
import tempfile
import unittest
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from flange_export import rows_to_tsv, write_xlsx


class TsvTest(unittest.TestCase):
    def test_header_and_values(self):
        rows = [{'DN': '50', 'D': '165'}, {'DN': '80', 'D': '200'}]
        text = rows_to_tsv(rows, ['DN', 'D'])
        self.assertEqual(text, 'DN\tD\n50\t165\n80\t200\n')

    def test_tabs_and_newlines_are_flattened(self):
        rows = [{'备注': 'a\tb\nc'}]
        text = rows_to_tsv(rows, ['备注'])
        self.assertNotIn('\t', text.splitlines()[1])
        self.assertIn('a b c', text)


class XlsxTest(unittest.TestCase):
    def test_minimal_workbook_structure(self):
        rows = [{'DN': '50', 'D': '165', '名称': 'A&B'},
                {'DN': '80', 'D': '-', '名称': ''}]
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'out.xlsx')
            write_xlsx(path, rows, ['DN', 'D', '名称'])
            with zipfile.ZipFile(path) as zf:
                names = set(zf.namelist())
                for required in ('[Content_Types].xml', 'xl/workbook.xml',
                                 'xl/worksheets/sheet1.xml', 'xl/styles.xml'):
                    self.assertIn(required, names)
                sheet = zf.read('xl/worksheets/sheet1.xml').decode('utf-8')
                workbook = zf.read('xl/workbook.xml').decode('utf-8')
        self.assertIn('DN', sheet)
        self.assertIn('<v>50</v>', sheet)
        self.assertIn('<v>165</v>', sheet)
        self.assertIn('A&amp;B', sheet)
        self.assertIn('查询结果', workbook)

    def test_empty_values_are_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'empty.xlsx')
            write_xlsx(path, [{'D': '-', '名称': ''}], ['D', '名称'])
            with zipfile.ZipFile(path) as zf:
                sheet = zf.read('xl/worksheets/sheet1.xml').decode('utf-8')
        self.assertNotIn('<v>-</v>', sheet)


if __name__ == '__main__':
    unittest.main()
