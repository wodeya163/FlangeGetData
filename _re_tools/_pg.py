p=r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py"
s=open(p,encoding="utf-8-sig").read()
a="""        b_d1 = best[0]
        b_d2 = best[1]"""
assert a in s
open(p,"w",encoding="utf-8",newline="").write(s.replace(a,"        b_d1, b_d2 = best[0], best[1]",1))
print("ok")
