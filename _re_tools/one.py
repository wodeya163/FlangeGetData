import dis, marshal, sys, types
def load(p): return marshal.loads(open(p,"rb").read()[16:])
def walk(code, prefix=""):
    name = prefix + ("" if code.co_name=="<module>" else code.co_name)
    yield name, code
    for c in code.co_consts:
        if isinstance(c, types.CodeType): yield from walk(c, name+".")
root = load(sys.argv[1]); target = sys.argv[2]; ln = int(sys.argv[3])
for n,c in walk(root):
    if n.lstrip(".")==target.lstrip(".") and c.co_firstlineno==ln:
        skip={"RESUME","CACHE","PRECALL","NOP","EXTENDED_ARG"}
        for ins in dis.get_instructions(c):
            if ins.opname in skip: continue
            a=ins.argval
            if isinstance(a,types.CodeType): a="<code %s>"%a.co_name
            print("%-26s %s"%(ins.opname,repr(a) if isinstance(a,(int,str,float,tuple,type(None))) else a))
        raise SystemExit(0)
print("not found")