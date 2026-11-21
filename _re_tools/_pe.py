p=r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py"
s=open(p,encoding="utf-8-sig").read()
a="""        self.lamp_comp_dot = None
        self.lamp_comp_txt = None
        self.lamp_st_dot = None
        self.lamp_st_txt = None
        self.lamp_br_dot = None
        self.lamp_br_txt = None"""
b="""        self.lamp_comp_dot = self.lamp_comp_txt = None
        self.lamp_st_dot = self.lamp_st_txt = None
        self.lamp_br_dot = self.lamp_br_txt = None"""
assert a in s
open(p,"w",encoding="utf-8",newline="").write(s.replace(a,b,1))
print("ok")
