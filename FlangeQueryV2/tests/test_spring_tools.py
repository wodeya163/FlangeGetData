# -*- coding: utf-8 -*-
"""弹簧设计计算回归。"""

import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.spring_calc import (design_compression, design_tension,
                              design_torsion)
from core.spring_data import MATERIALS, material_kinds, materials_by_kind
from core.spring_export import build_compression_mesh, mesh_stats, export_compression
from core.gear_stp import find_python


class SpringToolsTest(unittest.TestCase):
    def setUp(self):
        self.material = MATERIALS[0]

    def test_material_library(self):
        self.assertGreaterEqual(len(MATERIALS), 40)
        self.assertIn('carbon', material_kinds())
        self.assertTrue(materials_by_kind('stainless'))

    def test_compression_design(self):
        r = design_compression(100, 20, 20, self.material, 'static',
                               None, None, True)
        self.assertEqual(r['type'], 'compression')
        self.assertGreater(r['d'], 0)
        self.assertGreater(r['D'], r['d'])
        self.assertGreater(r['n'], 0)
        self.assertGreater(r['safety'], 0)

    def test_tension_design(self):
        r = design_tension(100, 20, 20, self.material, 'static',
                           None, None, True)
        self.assertEqual(r['type'], 'tension')
        self.assertGreater(r['allow_factor'], 0)

    def test_spring_mesh_and_stl(self):
        r = design_compression(100, 20, 20, self.material, 'static',
                               None, None, True)
        verts, faces = build_compression_mesh(
            r['d'], r['D'], r['n'], r['H0'], r['n1'])
        stats = mesh_stats(verts, faces)
        self.assertTrue(stats['manifold'])
        self.assertGreater(stats['volume'], 0)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, 'spring.stl')
            export_compression(r, path)
            self.assertGreater(os.path.getsize(path), 1000)
            with open(path, 'rb') as fh:
                self.assertGreater(len(fh.read(84)), 0)

    @unittest.skipUnless(os.environ.get('RUN_CADQUERY_TESTS'),
                         '设置 RUN_CADQUERY_TESTS=1 运行 STEP 测试')
    def test_step_export_if_cadquery_available(self):
        if not find_python(False):
            self.skipTest('未安装 CadQuery/OCP')
        r = design_compression(100, 20, 20, self.material, 'static',
                               None, None, True)
        tmp = tempfile.mkdtemp(dir=ROOT)
        try:
            path = os.path.join(tmp, 'spring.step')
            export_compression(r, path)
            self.assertGreater(os.path.getsize(path), 10000)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_torsion_design(self):
        r = design_torsion(10000, 1000, 30, self.material, 'static',
                           None, None, True)
        self.assertEqual(r['type'], 'torsion')
        self.assertGreater(r['sigma_max'], 0)
        self.assertGreater(r['angle_actual'], 0)


if __name__ == '__main__':
    unittest.main()
