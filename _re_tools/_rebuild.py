import io,re
root=r"E:\AI作品\work\FlangeGetData"
cur=io.open(root+r"\_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py",encoding="utf-8").read()
marker="        rng = compression_range(d2, seal_type)\n"
i=cur.rindex(marker)
head=cur[:i]
out=io.open(root+r"\_re_tools\out2\seal_ui.py",encoding="utf-8-sig").read()

show_tail = r'''        rng = compression_range(d2, seal_type)
        if rng:
            (w_min, w_max, label) = rng
            gi.append(f'''+"'''"+r'''压缩率推荐带：{w_min}%~{w_max}%（{label}，附录A资料性）'''+"'''"+r''')
'''

# build show_tail using concatenation to avoid nested triple quotes
show_tail = (
"        rng = compression_range(d2, seal_type)\n"
"        if rng:\n"
"            (w_min, w_max, label) = rng\n"
"            gi.append(f'''压缩率推荐带：{w_min}%~{w_max}%（{label}，附录A资料性）''')\n"
"        else:\n"
"            w_min = w_max = None\n"
"            gi.append('压缩率推荐带：本工况标准未收录，暂无数据（—）')\n"
"        actual_w = ((groove['d2'] - groove['h']) / groove['d2']) * 100\n"
"        gi.append(f'''实际压缩率：{actual_w:.1f}%''')\n"
"        self.ro_t_val.setText(f'''{groove['h']:.2f}''')\n"
"        self.ro_b_val.setText(f'''{groove['b']:.2f}''')\n"
"        self.ro_comp_val.setText(f'''{actual_w:.1f}%''')\n"
"        if w_min is None:\n"
"            _set_lamp(self.lamp_comp_dot, self.lamp_comp_txt, 'info', f'''压缩率 {actual_w:.1f}%：本工况标准未收录推荐带''')\n"
"        elif actual_w < w_min:\n"
"            _set_lamp(self.lamp_comp_dot, self.lamp_comp_txt, 'bad', f'''压缩率 {actual_w:.1f}% 低于推荐带（{w_min}%~{w_max}%）''')\n"
"        elif actual_w > w_max:\n"
"            _set_lamp(self.lamp_comp_dot, self.lamp_comp_txt, 'bad', f'''压缩率 {actual_w:.1f}% 高于推荐带（{w_min}%~{w_max}%）''')\n"
"        else:\n"
"            _set_lamp(self.lamp_comp_dot, self.lamp_comp_txt, 'ok', f'''压缩率 {actual_w:.1f}% 在推荐带内（{w_min}%~{w_max}%）''')\n"
"        if w_min is None:\n"
"            pass\n"
"        elif actual_w < w_min:\n"
"            gi.append(f'''⚠ 压缩率低于推荐带（{w_min}%~{w_max}%），密封力偏小，需结合工况确认''')\n"
"        elif actual_w > w_max:\n"
"            gi.append(f'''⚠ 压缩率高于推荐带（{w_min}%~{w_max}%），压缩损伤风险偏大，需结合工况确认''')\n"
"        else:\n"
"            gi.append(f'''✓ 压缩率在推荐带内（{w_min}%~{w_max}%）''')\n"
"        if groove['double_backup']:\n"
"            gi.append('已含双挡圈槽宽（b2）')\n"
"        elif groove['with_backup']:\n"
"            gi.append('已含单挡圈槽宽（b1）')\n"
"        gi.append('槽深非强制值：非标沟槽可由供需协商确定（第1章）')\n"
"        if dir_key in ('internal', 'external'):\n"
"            info = axial_row_info(d1, d2, dir_key, self.d7d8_input.text())\n"
"            self.axial_row_lbl.setText(info['label'])\n"
"            self.d7d8_hint.setText(info['hint'])\n"
"            gi.extend(info['gi'])\n"
"            self.groove_widget.set_axial_info(info['gi'][0] if info['gi'] else '')\n"
"        else:\n"
"            self.groove_widget.set_axial_info('')\n"
"        self.groove_info.setPlainText('\\n'.join(gi))\n"
"        return None\n"
)

doq_tail = (
"        dir_key = self._dir_key()\n"
"        if dir_key in ('internal', 'external'):\n"
"            d1_txt = self.d1_input.text().strip()\n"
"            d1_val = None\n"
"            if d1_txt:\n"
"                try:\n"
"                    d1_val = float(d1_txt)\n"
"                except ValueError:\n"
"                    lines.append(f'''O型圈内径 d1：「{d1_txt}」不是数字，无法计算 d7/d8 界限''')\n"
"            else:\n"
"                lines.append('沟槽直径 d7/d8：填入 O 型圈内径 d1 后给出界限值（式(3)/式(4)）')\n"
"            info = axial_row_info(d1_val, d2, dir_key, self.d7d8_input.text())\n"
"            lines.extend(info['gi'])\n"
"        if groove['double_backup']:\n"
"            lines.append('已含双挡圈槽宽（b2，图3右侧）')\n"
"        elif groove['with_backup']:\n"
"            lines.append('已含单挡圈槽宽（b1，图3左侧）')\n"
"        lines.append('槽深为标准推荐值（5.1.1注：允许按实际需要选定）；非标沟槽可由供需协商确定（第1章）')\n"
"        self.info.setPlainText('\\n'.join(lines))\n"
"        self._has_query = True\n"
)

paint_tail = (
"        rng = compression_range(d2, seal_type)\n"
"        actual_w = ((d2 - h_mm) / d2) * 100\n"
"        if rng:\n"
"            (w_min, w_max, _wl) = rng\n"
"            comp_color = GREEN if w_min <= actual_w <= w_max else RED\n"
"            comp_text = f'''压缩率 {actual_w:.1f}%（推荐带 {w_min}%~{w_max}%）'''\n"
"        else:\n"
"            comp_color = TEXT\n"
"            comp_text = f'''压缩率 {actual_w:.1f}%（本工况无标准推荐带）'''\n"
"        p.setPen(QColor(comp_color))\n"
"        p.setFont(QFont('Microsoft YaHei', 9, QFont.Weight.Bold))\n"
"        p.drawText(int(ML), 2, w - ML, 16, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, comp_text)\n"
"        p.setPen(QColor(SEC['edge_mid']))\n"
"        p.setFont(QFont('Microsoft YaHei', 7))\n"
"        p.drawText(int(cx - 30), int((4 + y0) / 2 + 3), 60, 12, Qt.AlignmentFlag.AlignCenter, top_name)\n"
"        p.drawText(int(w - MR - 78), int(h - 16), 78, 12, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, bot_name)\n"
"        p.setPen(QColor(SEC['note']))\n"
"        p.setFont(QFont('Microsoft YaHei', 7))\n"
"        p.drawText(int(w - MR - 240), 2, 240, 14, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, '尺寸按真比例；圈面积守恒；外形示意')\n"
"        if seal_type == 'static_axial' and self.axial_info:\n"
"            p.setPen(QColor(TEXT2))\n"
"            p.setFont(QFont('Microsoft YaHei', 7))\n"
"            p.drawText(int(ML), 18, w - ML - MR, 12, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.axial_info)\n"
"        depth_sym = 'h' if seal_type == 'static_axial' else 't'\n"
"        p.setPen(QColor(TEXT))\n"
"        p.setFont(QFont('Consolas', 9))\n"
"        hx = ML - 14\n"
"        p.drawLine(int(hx), int(shaft_top), int(hx), int(groove_bot))\n"
"        p.drawLine(int(hx - 4), int(shaft_top), int(hx + 4), int(shaft_top))\n"
"        p.drawLine(int(hx - 4), int(groove_bot), int(hx + 4), int(groove_bot))\n"
"        p.drawText(int(0), int((shaft_top + groove_bot) / 2 - 5), int(hx - 6), 10, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f'''{depth_sym}={h_mm:.2f}''')\n"
"        by = groove_bot + 12\n"
"        p.setPen(QColor(TEXT2))\n"
"        p.drawLine(int(gx1), int(groove_bot + 2), int(gx1), int(by))\n"
"        p.drawLine(int(gx2), int(groove_bot + 2), int(gx2), int(by))\n"
"        p.drawLine(int(gx1), int(by), int(gx2), int(by))\n"
"        p.drawText(int(cx - 30), int(by + 2), 60, 12, Qt.AlignmentFlag.AlignCenter, f'''b={b_mm:.2f}''')\n"
"        p.setPen(QColor(SEC['ring_note']))\n"
"        p.setFont(QFont('Consolas', 8, QFont.Weight.Bold))\n"
"        p.drawText(int(gx2 + 6), int(ring_y + ring_h_px / 2 - 14), 110, 10, Qt.AlignmentFlag.AlignLeft, f'''d₂={d2}''')\n"
"        p.drawText(int(gx2 + 6), int(ring_y + ring_h_px / 2 - 2), 110, 10, Qt.AlignmentFlag.AlignLeft, f'''圈宽≈{ring_w_mm:.2f}''')\n"
"        side_clear = (b_mm - ring_w_mm) / 2\n"
"        if side_clear > 0:\n"
"            p.setFont(QFont('Consolas', 8))\n"
"            p.drawText(int(gx2 + 6), int(ring_y + ring_h_px / 2 + 10), 130, 10, Qt.AlignmentFlag.AlignLeft, f'''侧隙≈{side_clear:.2f}（估算）''')\n"
"        wy = by + 12\n"
"        if wy < h - 14:\n"
"            p.setPen(QColor(SEC['ring_note']))\n"
"            rw1 = cx - ring_w_mm * scale / 2\n"
"            rw2 = cx + ring_w_mm * scale / 2\n"
"            p.drawLine(int(rw1), int(groove_bot + 2), int(rw1), int(wy))\n"
"            p.drawLine(int(rw2), int(groove_bot + 2), int(rw2), int(wy))\n"
"            p.drawLine(int(rw1), int(wy), int(rw2), int(wy))\n"
"            p.setFont(QFont('Consolas', 8, QFont.Weight.Bold))\n"
"            p.drawText(int(cx - 40), int(wy + 2), 80, 12, Qt.AlignmentFlag.AlignCenter, f'''圈宽≈{ring_w_mm:.2f}''')\n"
"        if gap_mm > 0:\n"
"            p.setPen(QColor(ORANGE))\n"
"            p.setFont(QFont('Consolas', 8))\n"
"            p.drawText(int(x2 - 90), int(y0 - 3), 90, 10, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, f'''g={gap_mm}（示意）''')\n"
"        dir_note = {\n"
"            'unidirectional': '单向压力 →',\n"
"            'alternating': '↔ 交替压力',\n"
"            'internal': '受内压 →',\n"
"            'external': '← 受外压' }.get(pdir)\n"
"        if dir_note:\n"
"            p.setPen(QColor(ORANGE))\n"
"            p.setFont(QFont('Microsoft YaHei', 8))\n"
"            p.drawText(int(ML), int(h - 16), 200, 12, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, dir_note)\n"
"        p.end()\n"
)

# GrooveTab block
gt = out[out.index("class GrooveTab:"):out.index("class MaterialTab:")]
gt = gt.replace("class GrooveTab:","class GrooveTab(QWidget):")
gt = gt.replace("        None((lambda : self._sync_dir_combo()))\n","        self.type_combo.currentTextChanged.connect(lambda _: self._sync_dir_combo())\n")
gt = gt.replace("        axial = None in self.type_combo.currentText()","        axial = '轴向' in self.type_combo.currentText()")
gt = gt.replace("        groove = calc_groove(d2, seal_type, backup_idx == 1, backup_idx == 2, self._dir_key(), **('seal_type', 'with_backup', 'double_backup', 'pressure_dir'))",
                "        groove = calc_groove(d2, seal_type=seal_type, with_backup=backup_idx == 1, double_backup=backup_idx == 2, pressure_dir=self._dir_key())")
gt = gt.replace("        actual_w = ((None - groove['h']) / d2) * 100","        actual_w = ((d2 - groove['h']) / d2) * 100")
gt = gt.replace("            '槽宽公差 +0.25/0（表3）；' + '轴向槽深h公差 +0.05/+0.10/0，按线径（表3）' if type_idx == 3 else '径向槽深t由缸内径H8/槽底h9按式(1)(2)确定（表3、5.1.2）',",
                "            '槽宽公差 +0.25/0（表3）；' + ('轴向槽深h公差 +0.05/+0.10/0，按线径（表3）' if type_idx == 3 else '径向槽深t由缸内径H8/槽底h9按式(1)(2)确定（表3、5.1.2）'),")
k=gt.index("        dir_key = self._dir_key()\n    # WARNING")
gt=gt[:k]+doq_tail
assert "None(" not in gt, [l for l in gt.splitlines() if "None(" in l]

rest = out[out.index("class MaterialTab:"):]
rest = rest.replace("class MaterialTab:","class MaterialTab(QWidget):")
rest = rest.replace("        for code, m in enumerate(mats):","        for i, (code, m) in enumerate(mats):")
rest = rest.replace("        None.result_table.setRowCount(len(results))","        self.result_table.setRowCount(len(results))")
rest = rest.replace("        for code, reason in enumerate(results):","        for i, (code, reason) in enumerate(results):")
rest = rest.replace("        self.all_btn.setText('📋 全部材料速览（8种） ' + '▾' if vis else '▸')","        self.all_btn.setText('📋 全部材料速览（8种） ' + ('▾' if vis else '▸'))")
rest = rest.replace("class KnowledgeTab:","class KnowledgeTab(QWidget):")
rest = rest.replace("class MainWindow:","class MainWindow(QMainWindow):")
rest = rest.replace("        None(theme.current())","        sync_colors(theme.current())")
rest = rest.replace("class GrooveWidget:","class GrooveWidget(QWidget):")
rest = rest.replace("        self.gap = 0\n","        self.gap = 0.0\n")
rest = rest.replace("        if not gap_mm:\n            pass\n        self.gap = 0\n","        self.gap = gap_mm or 0.0\n")
rest = rest.replace("        if not text:\n            pass\n        self.axial_info = ''\n","        self.axial_info = text or ''\n")
rest = rest.replace("    __classcell__ = None\n","")

# paintEvent fixes in rest
rest = rest.replace("        w = self.width()\n        h = self.height()\n","        w, h = self.width(), self.height()\n")
rest = rest.replace("        g = None.groove\n","        g = self.groove\n")
rest = rest.replace("        if p_mpa is not None:\n            pass\n        pressurized = not (p_mpa <= 0)\n","        pressurized = not (p_mpa is not None and p_mpa <= 0)\n")
rest = rest.replace("math.gamma(1.33333)","math.gamma(1.3333333333333333)").replace("math.gamma(1.66667)","math.gamma(1.6666666666666667)")
rest = rest.replace("        scale_h = (h * 0.84 - y0) / (h_mm + gap_mm if gap_mm > 0 else 0)\n","        scale_h = (h * 0.84 - y0) / (h_mm + (gap_mm if gap_mm > 0 else 0))\n")
rest = rest.replace("        gap_px = scale * gap_mm if gap_mm > 0 else 0\n","        gap_px = scale * gap_mm if gap_mm > 0 else 0.0\n")
rest = rest.replace("        gap_draw = max(gap_px, 3) if gap_mm > 0 else 0\n","        gap_draw = max(gap_px, 3.0) if gap_mm > 0 else 0.0\n")
rest = rest.replace("        gx1 = cx - b_px / 2\n        gx2 = cx + b_px / 2\n","        gx1, gx2 = cx - b_px / 2, cx + b_px / 2\n")
rest = rest.replace("        x1 = ML\n        x2 = w - MR\n","        x1, x2 = ML, w - MR\n")
rest = rest.replace("        QBrush = QBrush\n        import PySide6.QtGui\n","        from PySide6.QtGui import QBrush\n")
rest = rest.replace("        QPolygonF = QPolygonF\n        import PySide6.QtGui\n","        from PySide6.QtGui import QPolygonF\n")
rest = rest.replace("        ring_h_px = (groove_bot - y0) + 1 if gap_mm > 0 else 0\n","        ring_h_px = (groove_bot - y0) + (1 if gap_mm > 0 else 0)\n")
rest = rest.replace("        bk_w = 0\n","        bk_w = 0.0\n")
rest = rest.replace("                bk_w = max(6, free / 2)\n","                bk_w = max(6.0, free / 2)\n")
rest = rest.replace("            ext = min(26, x2 - gx2 - 6) if hp_side == 1 else min(26, gx1 - x1 - 6)\n","            ext = min(26.0, x2 - gx2 - 6) if hp_side == 1 else min(26.0, gx1 - x1 - 6)\n")
rest = rest.replace("        ring_x = ring_cx - ring_w_px / 2\n        ring_y = y0\n","        ring_x, ring_y = ring_cx - ring_w_px / 2, y0\n")
rest = rest.replace("        ring_cy = y0 + ring_h_px / 2\n        _apx = ring_w_px / 2\n        _bpx = ring_h_px / 2\n","        ring_cy = y0 + ring_h_px / 2.0\n        _apx, _bpx = ring_w_px / 2.0, ring_h_px / 2.0\n")
rest = rest.replace("0.666667","0.6666666666666666")
rest = rest.replace("            head = 6 if chan_h >= 14 else 4\n","            head = 6.0 if chan_h >= 14 else 4.0\n")
rest = rest.replace("        def arrow_h(x_from, y, x_to, head):","        def arrow_h(x_from, y, x_to, head=6.0):")
rest = rest.replace("        def arrow_v(x, y_from, y_to, head):","        def arrow_v(x, y_from, y_to, head=6.0):")
rest = rest.replace("            None.drawText(","            p.drawText(")

# paintEvent tail
j=rest.rindex("        rng = compression_range(d2, seal_type)\n")
rest=rest[:j]+paint_tail

new=head+show_tail+gt+rest
io.open(root+r"\_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py","w",encoding="utf-8",newline="\n").write(new)
print("lines",len(new.splitlines()))
