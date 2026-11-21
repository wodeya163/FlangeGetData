import io
p=r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py"
s=io.open(p,encoding="utf-8").read()
s=s.replace("        actual_w = ((None - groove['h']) / d2) * 100\n",
            "        actual_w = ((d2 - groove['h']) / d2) * 100\n")
old="""            '槽宽公差 +0.25/0（表3）；' + '轴向槽深h公差 +0.05/+0.10/0，按线径（表3）' if type_idx == 3 else '径向槽深t由缸内径H8/槽底h9按式(1)(2)确定（表3、5.1.2）',
"""
new="""            '槽宽公差 +0.25/0（表3）；' + ('轴向槽深h公差 +0.05/+0.10/0，按线径（表3）' if type_idx == 3 else '径向槽深t由缸内径H8/槽底h9按式(1)(2)确定（表3、5.1.2）'),
"""
assert old in s
s=s.replace(old,new)
old2="""        dir_key = self._dir_key()
    # WARNING: Decompyle incomplete
class MaterialTab(QWidget):
"""
new2="""        dir_key = self._dir_key()
        if dir_key in ('internal', 'external'):
            d1_txt = self.d1_input.text().strip()
            d1_val = None
            if d1_txt:
                try:
                    d1_val = float(d1_txt)
                except ValueError:
                    lines.append(f'''O型圈内径 d1：「{d1_txt}」不是数字，无法计算 d7/d8 界限''')
            else:
                lines.append('沟槽直径 d7/d8：填入 O 型圈内径 d1 后给出界限值（式(3)/式(4)）')
            info = axial_row_info(d1_val, d2, dir_key, self.d7d8_input.text())
            lines.extend(info['gi'])
        if groove['double_backup']:
            lines.append('已含双挡圈槽宽（b2，图3右侧）')
        elif groove['with_backup']:
            lines.append('已含单挡圈槽宽（b1，图3左侧）')
        lines.append('槽深为标准推荐值（5.1.1注：允许按实际需要选定）；非标沟槽可由供需协商确定（第1章）')
        self.info.setPlainText('\\n'.join(lines))
        self._has_query = True
class MaterialTab(QWidget):
"""
assert old2 in s
s=s.replace(old2,new2)
io.open(p,"w",encoding="utf-8",newline="\n").write(s)
print("ok")
