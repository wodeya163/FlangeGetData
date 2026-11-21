import io
p=r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py"
s=io.open(p,encoding="utf-8").read()
a="        if pressurized and hp_side == 0 or double_bk:\n"
b="        if not pressurized or hp_side == 0 or double_bk:\n"
assert a in s
s=s.replace(a,b)
io.open(p,"w",encoding="utf-8",newline="\n").write(s)
print("ok")
