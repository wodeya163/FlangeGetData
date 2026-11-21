import dis,marshal
f=open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\theme.pyc","rb"); f.read(16); code=marshal.load(f)
def walk(c):
    for k in c.co_consts:
        if isinstance(k,type(c)):
            if k.co_name=="_on_pick":
                print("firstline",k.co_firstlineno)
                for ins in dis.get_instructions(k):
                    if ins.offset>=190: print(ins.offset, ins.starts_line, ins.opname, ins.argrepr)
            walk(k)
walk(code)
