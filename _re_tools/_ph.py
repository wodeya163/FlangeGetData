p=r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py"
s=open(p,encoding="utf-8-sig").read()
a="""        b_stretch = ((d - b_d1) / b_d1) * 100
        if seal_type not in ('static_radial', 'dynamic_recip', 'dynamic_rotate'):"""
b="""        b_stretch = ((d - b_d1) / b_d1) * 100
        if rod_mode:
            kmax = _precompression_limit(b_d1, seal_type)
            if kmax is None:
                _set_lamp(self.lamp_st_dot, self.lamp_st_txt, 'info', f'''预压缩率 {-b_stretch:.1f}%：表A.2未收录该内径档，暂无判据''')
            elif -b_stretch <= kmax:
                _set_lamp(self.lamp_st_dot, self.lamp_st_txt, 'ok', f'''预压缩率 {-b_stretch:.1f}% 在表A.2上限 {kmax}% 内''')
            else:
                _set_lamp(self.lamp_st_dot, self.lamp_st_txt, 'bad', f'''预压缩率 {-b_stretch:.1f}% 超出表A.2上限 {kmax}%''')
        else:
            ymax = _stretch_limit(b_d1)
            if ymax is None:
                _set_lamp(self.lamp_st_dot, self.lamp_st_txt, 'info', f'''拉伸率 {b_stretch:.1f}%：表A.1未收录该内径档，暂无判据''')
            elif _stretch_ok(b_stretch, ymax):
                _set_lamp(self.lamp_st_dot, self.lamp_st_txt, 'ok', f'''拉伸率 {b_stretch:.1f}% 在表A.1带内（上限 {ymax}%）''')
            else:
                _set_lamp(self.lamp_st_dot, self.lamp_st_txt, 'bad', f'''拉伸率 {b_stretch:.1f}% 超出表A.1上限 {ymax}%''')
        if seal_type not in ('static_radial', 'dynamic_recip', 'dynamic_rotate'):"""
assert a in s
open(p,"w",encoding="utf-8",newline="").write(s.replace(a,b,1))
print("ok")
