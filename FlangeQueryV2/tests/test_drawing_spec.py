# -*- coding: utf-8 -*-
"""DrawingSpec、矢量导出与 PageSpec 扩展测试。"""

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PyQt5.QtWidgets import QApplication  # noqa: E402

from core.page_spec import PageSpec  # noqa: E402
from drawspec.bellows import build_bellows_spec  # noqa: E402
from drawspec.fitting import (build_cap_spec, build_elbow_spec,
                              build_reducer_spec, build_tee_spec)  # noqa: E402
from drawspec.flange import build_flange_spec  # noqa: E402
from drawspec.gasket import build_gasket_spec  # noqa: E402
from drawspec.pipe import build_pipe_spec  # noqa: E402
from drawspec.seal import build_seal_spec  # noqa: E402
from drawspec.renderer import render_pixmap, save_pdf, save_svg  # noqa: E402
from drawspec.wall import wall_for  # noqa: E402
import main  # noqa: E402


class DrawingSpecTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def _row(self, csvf, **where):
        _head, rows = main.load_csv(os.path.join(ROOT, 'Data', csvf))
        return next(r for r in rows
                    if all(str(r.get(k)) == str(v) for k, v in where.items()))

    def test_flange_spec_and_vector_exports(self):
        row = self._row('HGT20592_带颈对焊.csv', DN='50', PN='16')
        spec = build_flange_spec(row, kind='WN', face='RF',
                                 standard='HG/T 20592-2009')
        self.assertIsNotNone(spec)
        self.assertGreater(len(spec.paths), 2)
        self.assertGreaterEqual(len(spec.dimensions), 4)
        pm = render_pixmap(spec)
        self.assertFalse(pm.isNull())
        with tempfile.TemporaryDirectory() as tmp:
            pdf = os.path.join(tmp, 'x.pdf')
            svg = os.path.join(tmp, 'x.svg')
            save_pdf(spec, pdf)
            save_svg(spec, svg)
            with open(pdf, 'rb') as fh:
                self.assertTrue(fh.read(4).startswith(b'%PDF'))
            with open(svg, encoding='utf-8') as fh:
                self.assertIn('<svg', fh.read(512))

    def test_elbow_spec(self):
        row = self._row('GB12459_弯头.csv', DN='50')
        spec = build_elbow_spec(row, angle=90, standard='GB/T 12459-2017')
        self.assertIsNotNone(spec)
        self.assertGreaterEqual(len(spec.dimensions), 3)

    def test_all_part_specs(self):
        cases = [
            (build_tee_spec, self._row('GB12459_三通.csv', DN='50')),
            (build_reducer_spec, self._row('GB12459_异径管.csv', DN='50')),
            (build_cap_spec, self._row('GB12459_管帽.csv', DN='50')),
            (build_gasket_spec, self._row('HGT20606_RF.csv', DN='50')),
            (build_pipe_spec, self._row('GB17395_普通钢管.csv', DN='50')),
            (build_bellows_spec, self._row('U_bellows.csv')),
            (build_seal_spec, self._row('mfm_RF.csv')),
        ]
        for fn, row in cases:
            with self.subTest(fn=fn.__name__):
                spec = fn(row)
                self.assertIsNotNone(spec, fn.__name__)
                self.assertGreaterEqual(len(spec.paths), 1, fn.__name__)

    def test_page_spec_extension(self):
        p = PageSpec('WN', 'x.csv', 'x.bmp', {})
        self.assertEqual(p.kind, '')
        self.assertEqual(p.filters, ())
        q = p.with_meta(kind='flange', drawing='flange:WN',
                        filters=(('PN', 'enum'),))
        self.assertEqual(q.kind, 'flange')
        self.assertEqual(q.drawing, 'flange:WN')
        self.assertEqual(q.filters, (('PN', 'enum'),))
        self.assertEqual(q.name, 'WN')

    def test_wall_series_lookup(self):
        row = self._row('GB12459_三通.csv', DN='50')
        self.assertGreater(wall_for(row, 'Sch40'), 0)
        self.assertGreater(wall_for(row, 'Sch80'),
                           wall_for(row, 'Sch40'))


if __name__ == '__main__':
    unittest.main()
