import dis,types
src=open(r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py",encoding="utf-8").read()
co=compile(src,"x","exec")
def find(c,n):
    for k in c.co_consts:
        if isinstance(k,types.CodeType):
            if k.co_name==n: return k
            r=find(k,n)
            if r: return r
f=find(co,"paintEvent")
print("cell",f.co_cellvars)
print("free",f.co_freevars)
for i in dis.get_instructions(f):
    if i.offset>40: break
    print(i.offset,i.opname,i.argrepr)
for k in f.co_consts:
    if isinstance(k,types.CodeType):
        print("nested",k.co_name,"free",k.co_freevars,"cell",k.co_cellvars)
