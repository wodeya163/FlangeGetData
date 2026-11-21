import io
p=r'E:\AI作品\work\FlangeGetData\FlangeQueryV2\tests\test_weight_page.py'
t=io.open(p,encoding='utf-8').read()
t=t.replace("        self.assertEqual(self.win.weight_page.kind, 'pipe')\n        res = self.win.weight_page.calculate()","        self.assertEqual(self.win.weight_page.kind, 'pipe')\n        self.win.weight_page.unit_price.setValue(5.0)\n        res = self.win.weight_page.calculate()")
t=t.replace("        self.assertNotEqual(self.win.weight_page.mass.text(), '—')\n        self.assertIsNotNone(self.win.weight_page.preview.pixmap())","        self.assertNotEqual(self.win.weight_page.mass.text(), '—')\n        self.assertGreater(res['price'], 0)\n        self.assertIn('采购价格', self.win.weight_page.price_result.text())\n        self.assertIsNotNone(self.win.weight_page.preview.pixmap())")
t=t.replace("        self.assertEqual(self.win.weight_page.kind, 'elbow')\n        res = self.win.weight_page.calculate()","        self.assertEqual(self.win.weight_page.kind, 'elbow')\n        res = self.win.weight_page.calculate()")
t=t.replace("        self.assertGreater(res['mass'], 0)\n        self.assertIsNotNone(self.win.weight_page.preview.pixmap())","        self.assertGreater(res['mass'], 0)\n        self.assertGreater(res['price'], 0)\n        self.assertIsNotNone(self.win.weight_page.preview.pixmap())",1)
t=t.replace("        self.assertEqual(mp.shape.currentText(), '板材')\n        self.assertGreater(mp.calculate()['mass'], 0)","        self.assertEqual(mp.shape.currentText(), '板材')\n        mp.price.setValue(5.0)\n        self.assertGreater(mp.calculate()['mass'], 0)\n        self.assertIn('采购价格', mp.price_line.text())")
io.open(p,'w',encoding='utf-8',newline='\n').write(t)
print('price tests')
