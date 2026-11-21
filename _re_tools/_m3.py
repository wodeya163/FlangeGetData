import dis, io
src = open(r"_decompiled_tools\密封圈选型工具V2.5\source\seal_data.py", encoding="utf-8").read()
c = compile(src, "seal_data.py", "exec")
ins = list(dis.get_instructions(c))
for i in range(320, min(len(ins), 378)):
    print(i, ins[i].offset, ins[i].opname, repr(ins[i].argval))
print("total", len(ins))
