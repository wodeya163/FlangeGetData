import dis, marshal, types
c = marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\theme.pyc","rb").read()[16:])
def find(c, name):
    if c.co_name == name: return c
    for k in c.co_consts:
        if isinstance(k, types.CodeType):
            r = find(k, name)
            if r: return r
orig = find(c, "_on_pick")
def rel(fn, n=26):
    ins = list(dis.get_instructions(fn))[-n:]
    base = ins[0].offset
    return [(i.opname, ("->%d" % ((i.argval-base)//2)) if (i.opcode in dis.hasjrel or i.opcode in dis.hasjabs) else i.argval) for i in ins]
t = rel(orig)
for k, v in enumerate(t):
    print(k, v)
