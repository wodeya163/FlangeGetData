import marshal,types,dis
co=marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb").read()[16:])
def walk(c,path=""):
    for k in c.co_consts:
        if isinstance(k,types.CodeType):
            p=path+"/"+k.co_name
            print(p, "args",k.co_varnames[:k.co_argcount], "cell",k.co_cellvars, "free",k.co_freevars, "flags",k.co_flags)
            walk(k,p)
walk(co)
