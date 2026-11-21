import marshal, types, sys, importlib.util, os

def load(path):
    return marshal.loads(open(path, "rb").read()[16:])

def walk(code, prefix=""):
    name = prefix + ("" if code.co_name == "<module>" else code.co_name)
    yield name, code
    for c in code.co_consts:
        if isinstance(c, types.CodeType):
            yield from walk(c, name + ".")

def find(root, dotted):
    for n, c in walk(root):
        if n.lstrip(".") == dotted.lstrip("."):
            return c
    return None

pyc, dotted, name, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
root = load(pyc)
code = find(root, dotted)
if code is None:
    print("not found"); raise SystemExit(2)
t = compile("def %s(*a, **k):\n    pass\n" % name, "<iso>", "exec")
consts = tuple(code if isinstance(c, types.CodeType) else c for c in t.co_consts)
mod = t.replace(co_consts=consts, co_filename=code.co_filename)
open(out, "wb").write(importlib.util.MAGIC_NUMBER + b"\0" * 12 + marshal.dumps(mod))
print("ok", out, "insns", len(code.co_code))

