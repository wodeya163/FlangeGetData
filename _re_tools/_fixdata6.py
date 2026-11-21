import io
p = r"_decompiled_tools\密封圈选型工具V2.5\source\seal_data.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace("BACKUP_RING_PRESSURE = 10\n", "BACKUP_RING_PRESSURE = 10.0\n")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
