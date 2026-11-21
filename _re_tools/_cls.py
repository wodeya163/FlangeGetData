import dis,marshal
co=marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb").read()[16:])
cls=[k for k in co.co_consts if isinstance(k,type(co)) and k.co_name in ("OringTab","GrooveWidget")]
for c in cls:
    print("==",c.co_name,"freevars",c.co_freevars,"cellvars",c.co_cellvars)
    ins=list(dis.get_instructions(c))
    for x in ins[-8:]: print("  ",x.offset,x.opname,x.argrepr)
print("super refs:")
for c in cls:
    for k in c.co_consts:
        if isinstance(k,type(c)):
            ops=[x for x in dis.get_instructions(k) if x.opname in ("LOAD_GLOBAL","LOAD_DEREF") and x.argval in ("super","__class__")]
            if ops: print(" ",c.co_name,k.co_name,[(x.opname,x.argval) for x in ops][:6])
