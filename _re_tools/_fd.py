import dis, io, marshal, sys, types, difflib
pyc, src, name = sys.argv[1], sys.argv[2], sys.argv[3]
def walk(c):
    yield c
    for k in c.co_consts:
        if isinstance(k, types.CodeType):
            yield from walk(k)
orig = None
for c in walk(marshal.loads(open(pyc,"rb").read()[16:])):
    if c.co_name == name:
        orig = c
        break
mod = compile(open(src, encoding="utf-8").read(), src, "exec")
new = None
for c in walk(mod):
    if c.co_name == name:
        new = c
        break
def txt(c):
    b = io.StringIO(); dis.dis(c, file=b); return b.getvalue().splitlines()
a, b = txt(orig), txt(new)
for line in difflib.unified_diff(a, b, "orig", "new", lineterm="", n=6):
    print(line)
