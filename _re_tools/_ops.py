import dis,marshal,collections
f=open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\theme.pyc","rb"); f.read(16); code=marshal.load(f)
def walk(c):
    for k in c.co_consts:
        if isinstance(k,type(c)):
            if k.co_name=="_on_pick":
                print(collections.Counter(i.opname for i in dis.get_instructions(k)))
            walk(k)
walk(code)
