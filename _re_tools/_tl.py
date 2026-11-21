import io
p = r"_decompiled_tools\密封圈选型工具V2.5\source\theme.py"
lines = io.open(p, encoding="utf-8").read().splitlines()
for i in range(216, 236):
    print("### LINE", i+1, len(lines[i]))
