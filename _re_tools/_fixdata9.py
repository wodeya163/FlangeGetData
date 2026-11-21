import io
p = r"_decompiled_tools\密封圈选型工具V2.5\source\seal_data.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace("    (14, 38.7, 6),\n    (40, 97.5, 5),", "    (14.0, 38.7, 6),\n    (40.0, 97.5, 5),")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
