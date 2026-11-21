import dis,marshal
orig=marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb").read()[16:])
new=compile(open(r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py",encoding="utf-8-sig").read(),"seal_ui.py","exec")
def flat(c,p=""):
    d={p+c.co_name: len(list(dis.get_instructions(c)))}
    for k in c.co_consts:
        if isinstance(k,type(c)): d.update(flat(k,p+c.co_name+"."))
    return d
o=flat(orig); n=flat(new)
for k in o:
    if k in n and o[k]!=n[k]: print(f"{k:55s} orig={o[k]:5d} new={n[k]:5d}")
