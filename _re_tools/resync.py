import os, sys, re, json, marshal, types, subprocess, tempfile, importlib.util

PYCDC = os.environ.get("PYCDC", r"C:\Users\Administrator\AppData\Local\Temp\pycdc-shak2-build\pycdc.exe")
STRIP = 0x04 | 0x08 | 0x20 | 0x80 | 0x200
MAGIC = importlib.util.MAGIC_NUMBER


def load(path):
    return marshal.loads(open(path, "rb").read()[16:])


def walk(code, prefix=""):
    name = prefix + ("" if code.co_name == "<module>" else code.co_name)
    yield name.lstrip("."), code
    for c in code.co_consts:
        if isinstance(c, types.CodeType):
            yield from walk(c, name + ".")


_TMPL = None
def _tmpl():
    global _TMPL
    if _TMPL is None:
        t = compile("def f(*a, **k):\n    pass\n", "<stub>", "exec")
        _TMPL = [c for c in t.co_consts if isinstance(c, types.CodeType)][0]
    return _TMPL


def make_stub(orig):
    t = _tmpl()
    return t.replace(
        co_name=orig.co_name, co_qualname=orig.co_qualname,
        co_argcount=orig.co_argcount, co_posonlyargcount=orig.co_posonlyargcount,
        co_kwonlyargcount=orig.co_kwonlyargcount, co_nlocals=orig.co_nlocals,
        co_flags=orig.co_flags & ~STRIP, co_varnames=orig.co_varnames,
        co_freevars=orig.co_freevars, co_cellvars=orig.co_cellvars,
        co_firstlineno=orig.co_firstlineno, co_consts=t.co_consts,
        co_names=(), co_filename=orig.co_filename,
        co_linetable=b"", co_exceptiontable=b"")


def is_class_body(code):
    return "__qualname__" in code.co_names and "__module__" in code.co_names


def stub_tree(code, targets):
    prefix = "" if code.co_name == "<module>" else code.co_name
    new, changed = [], False
    for c in code.co_consts:
        if isinstance(c, types.CodeType):
            sub = (prefix + "." + c.co_name).lstrip(".")
            if sub in targets:
                new.append(make_stub(c)); changed = True
            else:
                nc = stub_tree(c, targets)
                new.append(nc); changed = changed or (nc is not c)
        else:
            new.append(c)
    return code if not changed else code.replace(co_consts=tuple(new))


def pycdc(module):
    p = os.path.join(tempfile.gettempdir(), "resync.pyc")
    open(p, "wb").write(MAGIC + b"\0" * 12 + marshal.dumps(module))
    r = subprocess.run([PYCDC, p], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.stdout


def isolate(code):
    t = _tmpl()
    consts = tuple(code if isinstance(c, types.CodeType) else c for c in t.co_consts)
    return pycdc(t.replace(co_consts=consts, co_filename=code.co_filename))


def empty_defs(text):
    """Names of defs whose body is empty or truncated."""
    lines = text.splitlines()
    out = set()
    for i, l in enumerate(lines):
        m = re.match(r"^(\s*)(?:async\s+)?def\s+(\w+)\s*\(", l)
        if not m:
            continue
        indent, name = len(m.group(1)), m.group(2)
        j, has = i + 1, False
        while j < len(lines):
            s = lines[j]
            if not s.strip():
                j += 1; continue
            if len(s) - len(s.lstrip()) <= indent:
                break
            has = True
            break
        if not has:
            out.add(name)
    return out


def block(text, indent):
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(r"def\s", l)), None)
    if start is None:
        return None
    out = [(" " * indent + lines[start])]
    for l in lines[start + 1:]:
        out.append((" " * indent + l) if l.strip() else "")
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out)


def splice(text, name, body):
    lines = text.splitlines()
    pat = re.compile(r"^(\s*)(?:async\s+)?def\s+%s\s*\(" % re.escape(name))
    for i, l in enumerate(lines):
        m = pat.match(l)
        if not m:
            continue
        indent = len(m.group(1))
        j = i + 1
        while j < len(lines):
            s = lines[j]
            if not s.strip():
                j += 1; continue
            if len(s) - len(s.lstrip()) <= indent:
                break
            j += 1
        return "\n".join(lines[:i] + body.splitlines() + lines[j:]), True
    return text, False


def main():
    pyc, out = sys.argv[1], sys.argv[2]
    report = None
    if "--report" in sys.argv:
        report = sys.argv[sys.argv.index("--report") + 1]
    root = load(pyc)
    objs = dict(walk(root))
    order = sorted((p for p in objs if p), key=lambda p: objs[p].co_firstlineno)
    stubs, text, it = set(), "", 0
    for it in range(400):
        text = pycdc(stub_tree(root, stubs) if stubs else root)
        names = set(re.findall(r"(?m)^\s*(?:async\s+)?def\s+(\w+)\s*\(", text))
        bad = empty_defs(text)
        bad_paths = {p for p in order if objs[p].co_name in bad}
        missing = [p for p in order if p not in stubs and "<" not in p
                   and not is_class_body(objs[p])
                   and (objs[p].co_name not in names or p in bad_paths)]
        if not missing:
            break
        stubs.add(missing[0])
    spliced, failed = [], []
    for path in sorted(stubs, key=lambda p: objs[p].co_firstlineno):
        code = objs[path]
        idx = None
        for l in text.splitlines():
            m = re.match(r"^(\s*)(?:async\s+)?def\s+%s\s*\(" % re.escape(code.co_name), l)
            if m:
                idx = len(m.group(1)); break
        if idx is None:
            failed.append({"path": path, "why": "no def line"}); continue
        body = block(isolate(code), idx)
        if body is None:
            failed.append({"path": path, "why": "isolate empty"}); continue
        text, ok = splice(text, code.co_name, body)
        (spliced if ok else failed).append(path if ok else {"path": path, "why": "splice"})
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    info = {"pyc": pyc, "iterations": it + 1, "objects": len(objs),
            "stubbed": len(stubs), "spliced": len(spliced), "splice_failed": failed}
    if report:
        json.dump(info, open(report, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in info.items() if k != "splice_failed"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
