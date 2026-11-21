p=r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py"
s=open(p,encoding="utf-8-sig").read()
def rep(a,b):
    global s
    assert a in s,"MISS:"+a[:60]
    s=s.replace(a,b,1)
rep("""        self.type_combo.currentTextChanged.connect(lambda _: self._sync_dir_combo())
        for wgt, sig in ((self.t_min""","""        self.seal_combo.currentTextChanged.connect(lambda _: self._sync_dir_combo())
        for wgt, sig in ((self.t_min""")
rep("self.gap_input.setRange(0, 2)","self.gap_input.setRange(0.0, 2.0)")
rep("""        axial = None in self.type_combo.currentText()""","""        axial = '轴向' in self.type_combo.currentText()""")
rep("self.gap = gap_mm or 0\n","self.gap = gap_mm or 0.0\n")
rep("for code, reason in enumerate(results):","for i, (code, reason) in enumerate(results):")
open(p,"w",encoding="utf-8",newline="").write(s)
print("ok")
