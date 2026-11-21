p=r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py"
s=open(p,encoding="utf-8-sig").read()
def rep(a,b):
    global s
    assert a in s, a[:70]
    s=s.replace(a,b,1)
rep("""        return ('套筒（孔面）', '轴（沟槽侧）')
def axial_row_info""","""        return ('孔（衬套面）', '轴（沟槽侧）')
    return ('套筒（孔面）', '轴（沟槽侧）')
def axial_row_info""")
rep("def sync_colors(t):","def sync_colors(t=None):")
rep("def setup_theme(app, key):","def setup_theme(app, key=None):")
rep("def _lbl(text, role):","def _lbl(text, role=''):")
rep("        def arrow_h(x_from, y, x_to, head):","        def arrow_h(x_from, y, x_to, head=2):")
rep("        def arrow_v(x, y_from, y_to, head):","        def arrow_v(x, y_from, y_to, head=2):")
# rerender
rep("""        None.groove_widget.sync_from_theme()""","""        self.groove_widget.sync_from_theme()""")
# _toggle_adv tail
rep("""        self.adv_box.setVisible(checked)
        if checked:
            self.btn_adv.setText('更多参数 ▾')
            return None
        None(self.btn_adv.setText)""","""        self.adv_box.setVisible(checked)
        self.btn_adv.setText('更多参数 ▾' if checked else '更多参数 ▸')""")
# _update_adv_summary
rep("""        t_min = None.t_min.value()
        t_max = self.t_max.value()""","""        t_min, t_max = self.t_min.value(), self.t_max.value()""")
rep("""        if not t_min != -20 and t_max != 80 and self.fit_combo.currentIndex() != 0 and self.dir_combo.currentIndex() != 0 and gap != 0 and hard != 70:
            pass
        changed = self.medium_combo.currentIndex() != 0
        if changed:
            self.adv_summary.setStyleSheet(f'''color: {ACCENT}; font-size: 12px;''')
            return None
        None(f'''{self.adv_summary.setStyleSheet}{TEXT2}; font-size: 12px;''')""","""        changed = t_min != -20 or t_max != 80 or self.fit_combo.currentIndex() != 0 or self.dir_combo.currentIndex() != 0 or gap != 0 or hard != 70 or self.medium_combo.currentIndex() != 0
        self.adv_summary.setStyleSheet(f'''color: {ACCENT}; font-size: 12px;''' if changed else f'''color: {TEXT2}; font-size: 12px;''')""")
# _sync_dir_combo
rep("""        if not hasattr(self, 'seal_combo') or hasattr(self, 'dir_combo'):""","""        if not hasattr(self, 'seal_combo') or not hasattr(self, 'dir_combo'):""")
rep("""        if None in self.seal_combo.currentText():""","""        if '轴向' in self.seal_combo.currentText():""")
# _update_axial_row
rep("""        axial = None in self.seal_combo.currentText()""","""        axial = '轴向' in self.seal_combo.currentText()""")
rep("""        if not axial and self.adv_box.isVisible():""","""        if axial and not self.adv_box.isVisible():""")
rep("""        info = None(None, None, self._current_dir_key(), None)""","""        info = axial_row_info(None, None, self._current_dir_key(), None)""")
open(p,"w",encoding="utf-8",newline="").write(s)
print("ok")
