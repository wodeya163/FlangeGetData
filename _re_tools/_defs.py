import dis,marshal
co=marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb").read()[16:])
def walk(c,ind=0):
    ins=list(dis.get_instructions(c))
    for i,x in enumerate(ins):
        if x.opname=="MAKE_FUNCTION" and (x.arg or 0):
            # find preceding LOAD_CONST of code
            j=i-1
            while j>=0 and not (ins[j].opname=="LOAD_CONST" and isinstance(ins[j].argval,type(c))):
                j-=1
            fn=ins[j].argval.co_name if j>=0 else "?"
            # defaults are the last LOAD_CONST before code
            dflt=None
            k=j-1
            if x.arg & 1 and k>=0: dflt=ins[k].argval
            print(" "*ind, c.co_name, "->", fn, "arg", x.arg, "defaults", dflt)
    for k in c.co_consts:
        if isinstance(k,type(c)): walk(k,ind+1)
walk(co)
