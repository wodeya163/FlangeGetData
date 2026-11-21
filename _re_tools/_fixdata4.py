import io, re
p = r"_decompiled_tools\密封圈选型工具V2.5\source\seal_data.py"
s = io.open(p, encoding="utf-8").read()
s = re.sub(r"(?m)^    7: ", "    7.0: ", s)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
