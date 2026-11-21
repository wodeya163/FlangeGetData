import dis,marshal
co=marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb").read()[16:])
def find(c,n):
    for k in c.co_consts:
        if isinstance(k,type(c)):
            if k.co_name==n: return k
            r=find(k,n)
            if r: return r
def show(cls,fn,a,b):
    c=find(co,cls); f=[k for k in c.co_consts if isinstance(k,type(c)) and k.co_name==fn][0]
    print("==",cls,fn)
    for i,x in enumerate(dis.get_instructions(f)):
        if a<=i<=b: print(" ",i,x.offset,x.opname,x.argrepr)
show("OringTab","__init__",440,460)
show("GrooveTab","_update_axial_row",0,30)
show("GrooveTab","_update_axial_row",0,30)
show("MaterialTab","_do_recommend",80,110)
