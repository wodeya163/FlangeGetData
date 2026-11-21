import dis,marshal,importlib.util,sys
f=open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\theme.pyc","rb")
f.read(16); code=marshal.load(f)
def walk(c):
    for k in c.co_consts:
        if isinstance(k,type(c)):
            if k.co_name=="_on_pick":
                print("names",k.co_varnames)
                for i,ins in enumerate(dis.get_instructions(k)):
                    print(i, ins.offset, ins.opname, ins.argrepr, ins.argval)
            walk(k)
walk(code)
