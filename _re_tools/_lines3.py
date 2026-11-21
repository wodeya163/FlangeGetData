import dis,marshal
f=open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\theme.pyc","rb"); f.read(16); code=marshal.load(f)
def walk(c,ind=0):
    for k in c.co_consts:
        if isinstance(k,type(c)):
            lines=[i.starts_line for i in dis.get_instructions(k) if i.starts_line]
            print(" "*ind, k.co_name, "first",k.co_firstlineno,"lines",min(lines) if lines else None, max(lines) if lines else None, "decreases", sum(1 for a,b in zip(lines,lines[1:]) if b<a))
            walk(k,ind+2)
walk(code)
