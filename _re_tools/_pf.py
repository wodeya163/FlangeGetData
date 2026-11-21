p=r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py"
s=open(p,encoding="utf-8-sig").read()
a="""        for d1, d2, pri in None(candidates):
            stretch = ((d - d1) / d1) * 100
            self.result_table.setItem(i, 0, _mono(f'''{d1:.2f}'''))
            self.result_table.setItem(i, 1, _mono(f'''{d2:.2f}'''))
            self.result_table.setItem(i, 2, stretch_item)
"""
b="""        for i, (d1, d2, pri) in enumerate(candidates):
            stretch = ((d - d1) / d1) * 100
            self.result_table.setItem(i, 0, _mono(f'''{d1:.2f}'''))
            self.result_table.setItem(i, 1, _mono(f'''{d2:.2f}'''))
            if rod_mode:
                kmax = _precompression_limit(d1, seal_type)
                if kmax is None:
                    stretch_item = _mono(f'''{stretch:.1f}%''')
                    stretch_item.setToolTip('表A.2未收录该内径档或该档不适用本工况')
                elif -stretch <= kmax:
                    stretch_item = _mono(f'''预压缩{-stretch:.1f}%''')
                    stretch_item.setForeground(QColor(GREEN))
                    stretch_item.setToolTip(f'''在表A.2预压缩率上限 {kmax}% 内''')
                else:
                    stretch_item = _mono(f'''预压缩{-stretch:.1f}%''')
                    stretch_item.setForeground(QColor(RED))
                    stretch_item.setToolTip(f'''超出表A.2预压缩率上限 {kmax}%''')
            else:
                stretch_item = _mono(f'''{stretch:.1f}%''')
                ymax = _stretch_limit(d1)
                if ymax is None:
                    stretch_item.setToolTip('表A.1未收录该内径档，无标准推荐上限')
                elif _stretch_ok(stretch, ymax):
                    stretch_item.setForeground(QColor(GREEN))
                else:
                    stretch_item.setForeground(QColor(RED))
            self.result_table.setItem(i, 2, stretch_item)
"""
assert a in s
open(p,"w",encoding="utf-8",newline="").write(s.replace(a,b,1))
print("ok")
