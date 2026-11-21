import dis, marshal
c = marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_data.pyc","rb").read()[16:])
ins = list(dis.get_instructions(c))
for i in range(55, 85):
    print(i, ins[i].offset, ins[i].opname, repr(ins[i].argval))
