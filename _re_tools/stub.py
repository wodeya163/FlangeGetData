import marshal, types, sys, importlib.util, re

def load(path):
    return marshal.loads(open(path, "rb").read()[16:])

def walk(code, prefix=""):
    name = prefix + ("" if code.co_name == "<module>" else code.co_name)
    yield name.lstrip("."), code
    for c in code.co_consts:
        if isinstance(c, types.CodeType):
            yield from walk(c, name + ".")

_TMPL = None
def tmpl():
    global _TMPL
    if _TMPL is None:
        t = compile("def f():\n    pass\n", "<stub>", "exec")
        _TMPL = [c for c in t.co_consts if isinstance(c, types.CodeType)][0]
    return _TMPL

STRIP = 0x04 | 0x08 | 0x20 | 0x80 | 0x200

def make_stub(orig):
    return tmpl().replace(
        co_name=orig.co_name, co_qualname=orig.co_qualname,
        co_argcount=orig.co_argcount, co_posonlyargcount=orig.co_posonlyargcount,
        co_kwonlyargcount=orig.co_kwonlyargcount, co_nlocals=orig.co_nlocals,
        co_flags=orig.co_flags & ~STRIP,
        co_varnames=orig.co_varnames, co_freevars=orig.co_freevars,
        co_cellvars=orig.co_cellvars, co_firstlineno=orig.co_firstlineno,
        co_consts=(None,), co_names=(), co_filename=orig.co_filename,
        co_linetable=b"", co_exceptiontable=b"",
    )

def stub_tree(code, targets):
    """Return code with the code objects whose dotted name is in targets replaced by stubs."""
    prefix = "" if code.co_name == "<module>" else code.co_name
    newconsts = []
    changed = False
    for c in code.co_consts:
        if isinstance(c, types.CodeType):
            sub = (prefix + "." + c.co_name).lstrip(".")
            if sub in targets:
                newconsts.append(make_stub(c)); changed = True
            else:
                nc = stub_tree(c, targets)
                newconsts.append(nc); changed = changed or (nc is not c)
        else:
            newconsts.append(c)
    if not changed:
        return code
    return code.replace(co_consts=tuple(newconsts))

pyc, outp = sys.argv[1], sys.argv[2]
targets = set(sys.argv[3:])
root = load(pyc)
new = stub_tree(root, targets)
open(outp, "wb").write(importlib.util.MAGIC_NUMBER + b"\0" * 12 + marshal.dumps(new))
print("stubbed:", ", ".join(sorted(targets)))
