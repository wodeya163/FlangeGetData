import marshal,types,dis,collections
O=marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb").read()[16:])
def find(c,n):
    for k in c.co_consts:
        if isinstance(k,types.CodeType):
            if k.co_name==n: return k
            r=find(k,n)
            if r: return r
src=open(r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py",encoding="utf-8").read()
N=compile(src,"x","exec")
o=find(O,"paintEvent"); n=find(N,"paintEvent")
def nums(c):
    co=collections.Counter()
    for k in c.co_consts:
        if isinstance(k,(int,float)) and not isinstance(k,bool): co[repr(k)]+=1
    for k in c.co_consts:
        if isinstance(k,types.CodeType):
            co.update(nums(k))
    return co
a,b=nums(o),nums(n)
print("only orig:",{k:v for k,v in a.items() if v!=b.get(k,0)})
print("only new :",{k:v for k,v in b.items() if v!=a.get(k,0)})
