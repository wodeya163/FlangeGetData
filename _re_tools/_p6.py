p=r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py"
s=open(p,encoding="utf-8-sig").read()
def rep(a,b):
    global s
    assert a in s, "MISS:"+a[:70]
    s=s.replace(a,b,1)
rep("""        self.all_btn.setText('📋 全部材料速览（8种） ' + '▾' if vis else '▸')""","""        self.all_btn.setText('📋 全部材料速览（8种） ' + ('▾' if vis else '▸'))""")
rep("""        for code, m in enumerate(mats):""","""        for i, (code, m) in enumerate(mats):""")
rep("""        None.result_table.setRowCount(len(results))""","""        self.result_table.setRowCount(len(results))""")
rep("""        None(theme.current())""","""        sync_colors(theme.current())""")
rep("""        if not gap_mm:
            pass
        self.gap = 0
        self.update()""","""        self.gap = gap_mm or 0
        self.update()""")
rep("""        if not text:
            pass
        self.axial_info = ''
        self.update()""","""        self.axial_info = text or ''
        self.update()""")
rep("""        self.gap = 0
        self.axial_info = ''""","""        self.gap = 0.0
        self.axial_info = ''""")
rep("self.d_input.setValue(20)","self.d_input.setValue(20.0)")
s=s.replace("""None((lambda : self._sync_dir_combo()))""","""self.type_combo.currentTextChanged.connect(lambda _: self._sync_dir_combo())""")
open(p,"w",encoding="utf-8",newline="").write(s)
print("ok")
