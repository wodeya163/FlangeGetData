import io
p=r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py"
s=io.open(p,encoding="utf-8").read()
a="        pressurized = not (p_mpa is None or p_mpa <= 0)\n"
b="        pressurized = not (p_mpa is not None and p_mpa <= 0)\n"
assert a in s
s=s.replace(a,b)
io.open(p,"w",encoding="utf-8",newline="\n").write(s)
print("ok")
