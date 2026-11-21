import dis,marshal
co=marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb").read()[16:])
def find(c,n):
    for k in c.co_consts:
        if isinstance(k,type(c)):
            if k.co_name==n: return k
            r=find(k,n)
            if r: return r
for cls in ("OringTab","GrooveTab"):
    c=find(co,cls); f=[k for k in c.co_consts if isinstance(k,type(c)) and k.co_name=="__init__"][0]
    ins=list(dis.get_instructions(f))
    for i,x in enumerate(ins):
        if x.argval=="currentTextChanged":
            for y in ins[i-3:i+9]: print(cls,i-3,y.offset,y.opname,y.argrepr)
            print("---")
