import io
p = r"_decompiled_tools\密封圈选型工具V2.5\source\seal_data.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace("    3.55: (2.9, 2.85, 2.95, 4.6, 4.8, 6.2, 7.6),", "    3.55: (2.9, 2.85, 2.95, 4.6, 4.8, 6.2, 7.6),")
s = s.replace("(4.31, 4.35, 4.5, 6.9, 7.1, 9, 10.9)", "(4.31, 4.35, 4.5, 6.9, 7.1, 9.0, 10.9)")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
