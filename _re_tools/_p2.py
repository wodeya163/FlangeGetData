import dis,marshal
co=marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb").read()[16:])
def find(c,n):
    for k in c.co_consts:
        if isinstance(k,type(c)):
            if k.co_name==n: return k
            r=find(k,n)
            if r: return r
sc=find(co,"sync_colors")
for i,x in enumerate(dis.get_instructions(sc)):
    if 30<=i<=60: print(i,x.offset,x.opname,x.argrepr)
print("=== module stores")
ins=list(dis.get_instructions(co))
for x in ins:
    if x.opname in ("STORE_GLOBAL","STORE_NAME") and x.offset<640:
        print(x.offset,x.opname,x.argval)
