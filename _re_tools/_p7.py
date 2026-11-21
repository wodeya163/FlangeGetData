import dis,marshal
co=marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb").read()[16:])
def find(c,n):
    for k in c.co_consts:
        if isinstance(k,type(c)):
            if k.co_name==n: return k
            r=find(k,n)
            if r: return r
for cls in ("OringTab","GrooveTab","GrooveWidget"):
    c=find(co,cls)
    for k in c.co_consts:
        if isinstance(k,type(c)) and k.co_name=="__init__":
            print("==",cls,"__init__ false line")
            for i,x in enumerate(dis.get_instructions(k)):
                if 140<=i<=170: print(" ",i,x.offset,x.opname,x.argrepr)
