import json, os, subprocess, sys, tempfile, marshal, types, importlib.util

PYCDC = os.environ.get("PYCDC", r"C:\Users\Administrator\AppData\Local\Temp\pycdc-shak2-build\pycdc.exe")
pyc, rep = sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8"))
def load(p): return marshal.loads(open(p, "rb").read()[16:])
def walk(code, prefix=""):
    n = prefix + ("" if code.co_name == "<module>" else code.co_name)
    yield n.lstrip("."), code
    for c in code.co_consts:
        if isinstance(c, types.CodeType): yield from walk(c, n + ".")
root = load(pyc); objs = dict(walk(root))
TMPL = [c for c in compile("def f(*a, **k):\n    pass\n", "<i>", "exec").co_consts if isinstance(c, types.CodeType)][0]
BASE = tuple(TMPL.co_consts)
ok = bad = err = 0; fails = []
for path in rep["stubbed"]:
    code = objs.get(path)
    if code is None:
        err += 1; continue
    consts = tuple(code if isinstance(c, types.CodeType) else c for c in BASE)
    mod = TMPL.replace(co_consts=consts, co_filename=code.co_filename)
    p = os.path.join(tempfile.gettempdir(), "iso_t.pyc")
    open(p, "wb").write(importlib.util.MAGIC_NUMBER + b"\0" * 12 + marshal.dumps(mod))
    r = subprocess.run([PYCDC, p], capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        compile(r.stdout, "<o>", "exec"); ok += 1
    except SyntaxError as e:
        bad += 1; fails.append((path, e.lineno, str(e.msg)))
print("isolated ok=%d syntax_bad=%d lookup_err=%d total=%d" % (ok, bad, err, len(rep["stubbed"])))
for f in fails[:30]: print("  BAD %-50s line %s: %s" % f)
