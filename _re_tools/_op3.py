import dis, marshal, types
c = marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\theme.pyc","rb").read()[16:])
def find(c, name):
    if c.co_name == name: return c
    for k in c.co_consts:
        if isinstance(k, types.CodeType):
            r = find(k, name)
            if r: return r
f = find(c, "_on_pick")
print(f.co_varnames, f.co_cellvars, f.co_freevars)
for i in dis.get_instructions(f):
    if 180 <= i.offset <= 300:
        print(i.offset, i.opname, repr(i.argval), i.starts_line or "")
