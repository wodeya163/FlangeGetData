import dis,marshal
f=open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb"); f.read(16); code=marshal.load(f)
def walk(c,ind=0):
    print(" "*ind, repr(c.co_name), "first",c.co_firstlineno, "varnames",c.co_varnames[:8], "nconst",len(c.co_consts))
    for k in c.co_consts:
        if isinstance(k,type(c)):
            walk(k,ind+2)
walk(code)
