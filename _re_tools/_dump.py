import dis,marshal,sys
co=marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb").read()[16:])
def find(c,n):
    for k in c.co_consts:
        if isinstance(k,type(c)):
            if k.co_name==n: return k
            r=find(k,n)
            if r: return r
for n in sys.argv[1:]:
    f=find(co,n); print("="*20,n)
    for x in dis.get_instructions(f): print(x.offset,x.opname,x.argrepr)
