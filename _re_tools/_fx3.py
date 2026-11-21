import io
p = r"_decompiled_tools\密封圈选型工具V2.5\source\seal_data.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace("def assess_backup_ring(pressure_mpa=None, gap_mm=None, hardness=None, temp_max=None):",
              "def assess_backup_ring(pressure_mpa, gap_mm=None, hardness=None, temp_max=None):")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
