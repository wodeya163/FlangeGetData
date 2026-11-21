import dis,marshal
co=marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb").read()[16:])
def find(c,n):
    for k in c.co_consts:
        if isinstance(k,type(c)):
            if k.co_name==n: return k
            r=find(k,n)
            if r: return r
pn=find(co,"part_names")
for x in dis.get_instructions(pn): print(x.offset,x.opname,x.argrepr)
print("=== module 215-240")
for i,x in enumerate(dis.get_instructions(co)):
    if 215<=i<=240: print(i,x.offset,x.opname,x.argrepr)
