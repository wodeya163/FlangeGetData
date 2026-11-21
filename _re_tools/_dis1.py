import dis,io
src=open(r"_decompiled_tools\密封圈选型工具V2.5\source\theme.py",encoding="utf-8-sig").read()
ns={}
code=compile(src,"x","exec")
def walk(c,depth=0):
    for k in c.co_consts:
        if isinstance(k,type(c)):
            if k.co_name=="_on_pick":
                for i,ins in enumerate(dis.get_instructions(k)):
                    if i>100: print(i, ins.offset, ins.opname, ins.argrepr, ins.argval)
            walk(k,depth+1)
walk(code)
