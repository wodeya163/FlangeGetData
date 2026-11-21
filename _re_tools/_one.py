import dis, sys
src = open(r"_decompiled_tools\密封圈选型工具V2.5\source\seal_data.py", encoding="utf-8").read()
mod = compile(src, "seal_data.py", "exec")
for c in mod.co_consts:
    if hasattr(c, "co_name") and c.co_name == "compression_range":
        dis.dis(c)
