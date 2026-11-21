import dis, marshal, sys, types, importlib.util

def load(p):
    d = open(p,"rb").read()
    return marshal.loads(d[16:])

def walk(code, prefix=""):
    name = prefix + ("" if code.co_name == "<module>" else code.co_name)
    yield name, code
    for c in code.co_consts:
        if isinstance(c, types.CodeType):
            yield from walk(c, name + ".")

pyc, dotted = sys.argv[1], sys.argv[2]
root = load(pyc)
code = None
for n, c in walk(root):
    if n.lstrip(".") == dotted.lstrip("."):
        code = c
        break
if code is None:
    print("not found"); raise SystemExit(2)
print("###", dotted, "args=", code.co_varnames[:code.co_argcount], "vars=", code.co_varnames[code.co_argcount:])
skip = {"RESUME","CACHE","PRECALL","NOP","EXTENDED_ARG","RETURN_GENERATOR","MAKE_CELL","COPY_FREE_VARS","PUSH_NULL"}
lines = None
for ins in dis.get_instructions(code):
    if ins.opname in skip: continue
    a = ins.argval
    if isinstance(a, types.CodeType): a = "<code %s>" % a.co_name
    if isinstance(a, float) or isinstance(a, (int,str,tuple)) or a is None:
        s = repr(a)
    else:
        s = str(a)
    print("%5s %-26s %s" % (ins.positions.lineno if ins.positions else "", ins.opname, s))