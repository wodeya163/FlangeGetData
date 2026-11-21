import dis,marshal
src=open(r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py",encoding="utf-8-sig").read()
c=compile(src,"seal_ui.py","exec")
def find(c,name):
    for k in c.co_consts:
        if isinstance(k,type(c)):
            if k.co_name==name: return k
            r=find(k,name)
            if r: return r
new=find(c,"axial_row_info")
old=marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb").read()[16:])
old=find(old,"axial_row_info")
for label,co in (("ORIG",old),("NEW",new)):
    print("==",label)
    for ins in dis.get_instructions(co):
        if 360<=ins.offset<=420: print(ins.offset,ins.opname,ins.argrepr)
