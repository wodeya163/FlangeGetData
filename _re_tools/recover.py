import marshal, types, sys, os, subprocess, importlib.util, json, re, tempfile

PYCDC = os.environ.get("PYCDC", r"C:\Users\Administrator\AppData\Local\Temp\pycdc-shak2-build\pycdc.exe")
STRIP = 0x04 | 0x08 | 0x20 | 0x80 | 0x200

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

def make_stub(orig):
    flags = orig.co_flags & ~STRIP
    if orig.co_name == "__init_subclass__" or orig.co_name == "__class_getitem__":
        pass
    return tmpl().replace(
        co_name=orig.co_name, co_qualname=orig.co_qualname,
        co_argcount=orig.co_argcount, co_posonlyargcount=orig.co_posonlyargcount,
        co_kwonlyargcount=orig.co_kwonlyargcount, co_nlocals=orig.co_nlocals,
        co_flags=flags, co_varnames=orig.co_varnames, co_freevars=orig.co_freevars,
        co_cellvars=orig.co_cellvars, co_firstlineno=orig.co_firstlineno,
        co_consts=(None,), co_names=(), co_filename=orig.co_filename,
        co_linetable=b"", co_exceptiontable=b"")

def is_class_body(code):
    return "__qualname__" in code.co_names and "__module__" in code.co_names

def stub_tree(code, targets):
    prefix = "" if code.co_name == "<module>" else code.co_name
    newconsts, changed = [], False
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
    return code if not changed else code.replace(co_consts=tuple(newconsts))

def run_pycdc(pyc_path):
    r = subprocess.run([PYCDC, pyc_path], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout

def main():
    pyc, out = sys.argv[1], sys.argv[2]
    report_path = None
    if "--report" in sys.argv:
        report_path = sys.argv[sys.argv.index("--report") + 1]
    root = load(pyc)
    objs = dict(walk(root))
    paths = [p for p in objs if p]
    stubs = set()
    text = ""
    tmp = os.path.join(tempfile.gettempdir(), "recover_work.pyc")
    for it in range(15):
        cur = stub_tree(root, stubs) if stubs else root
        open(tmp, "wb").write(importlib.util.MAGIC_NUMBER + b"\0" * 12 + marshal.dumps(cur))
        text = run_pycdc(tmp)
        defnames = set(re.findall(r"(?m)^\s*(?:async\s+)?def\s+(\w+)\s*\(", text))
        missing = []
        for p in paths:
            c = objs[p]
            if is_class_body(c):
                continue
            if c.co_name not in defnames:
                missing.append(p)
        new = set(missing) - stubs
        if not new:
            break
        stubs |= new
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    if report_path:
        json.dump({"pyc": pyc, "stubbed": sorted(stubs), "iterations": it + 1,
                   "objects": len(paths)}, open(report_path, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
    print("iterations=%d objects=%d stubbed=%d -> %s" % (it + 1, len(paths), len(stubs), out))

main()
