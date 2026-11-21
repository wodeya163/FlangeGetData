import dis,marshal
co=marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb").read()[16:])
def find(c,n):
    for k in c.co_consts:
        if isinstance(k,type(c)):
            if k.co_name==n: return k
            r=find(k,n)
            if r: return r
c=find(co,"OringTab"); f=[k for k in c.co_consts if isinstance(k,type(c)) and k.co_name=="__init__"][0]
for i,x in enumerate(dis.get_instructions(f)):
    if 825<=i<=862: print(i,x.offset,x.opname,x.argrepr)
