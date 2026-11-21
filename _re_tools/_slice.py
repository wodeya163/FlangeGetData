import dis,marshal,sys
co=marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb").read()[16:])
def find(c,n):
    for k in c.co_consts:
        if isinstance(k,type(c)):
            if k.co_name==n: return k
            r=find(k,n)
            if r: return r
f=find(co,sys.argv[1]); a,b=int(sys.argv[2]),int(sys.argv[3])
ins=list(dis.get_instructions(f))
for i in range(a,min(b,len(ins))): print(i,ins[i].offset,ins[i].opname,ins[i].argrepr)
