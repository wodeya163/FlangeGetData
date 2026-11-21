"""Rebuild a module: stub every method/function, decompile the skeleton, then splice isolated bodies back."""
import os, sys, re, json, marshal, types, subprocess, tempfile, importlib.util

PYCDC = os.environ.get("PYCDC", r"C:\Users\Administrator\AppData\Local\Temp\pycdc-shak2-build\pycdc.exe")
STRIP = 0x04 | 0x08 | 0x20 | 0x80 | 0x200
MAGIC = importlib.util.MAGIC_NUMBER


def load(p):
    return marshal.loads(open(p, "rb").read()[16:])


def walk(code, prefix="", out=None):
    if out is None:
        out = []
    name = (prefix + "." + code.co_name).lstrip(".") if prefix else code.co_name
    out.append((name, code))
    for c in code.co_consts:
        if isinstance(c, types.CodeType):
            walk(c, "" if code.co_name == "<module>" else name, out)
    return out


_MOD = None
def mod_tmpl():
    global _MOD
    if _MOD is None:
        _MOD = compile("def f(*a, **k):\n    pass\n", "<stub>", "exec")
    return _MOD


def tmpl():
    return [c for c in mod_tmpl().co_consts if isinstance(c, types.CodeType)][0]


def is_class(code):
    return "__qualname__" in code.co_names and "__module__" in code.co_names


def stub_of(orig):
    t = tmpl()
    return t.replace(
        co_name=orig.co_name, co_qualname=orig.co_qualname,
        co_argcount=orig.co_argcount, co_posonlyargcount=orig.co_posonlyargcount,
        co_kwonlyargcount=orig.co_kwonlyargcount, co_nlocals=orig.co_nlocals,
        co_flags=orig.co_flags & ~STRIP, co_varnames=orig.co_varnames,
        co_freevars=orig.co_freevars, co_cellvars=orig.co_cellvars,
        co_firstlineno=orig.co_firstlineno, co_consts=t.co_consts,
        co_names=(), co_filename=orig.co_filename,
        co_linetable=b"", co_exceptiontable=b"")


def stub_children(code):
    """Stub every direct code const (methods of a class body, functions of module)."""
    new, changed = [], False
    for c in code.co_consts:
        if isinstance(c, types.CodeType):
            if is_class(c):
                nc = stub_children(c)
                new.append(nc); changed = changed or (nc is not c)
            else:
                new.append(stub_of(c)); changed = True
        else:
            new.append(c)
    return code if not changed else code.replace(co_consts=tuple(new))


def run(module):
    p = os.path.join(tempfile.gettempdir(), "rb_work.pyc")
    with open(p, "wb") as fh:
        fh.write(MAGIC + b"\0" * 12 + marshal.dumps(module))
    r = subprocess.run([PYCDC, p], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.stdout


def isolate(code):
    t = mod_tmpl()
    consts = tuple(code if isinstance(c, types.CodeType) else c for c in t.co_consts)
    return run(t.replace(co_consts=consts, co_filename=code.co_filename))


def body_lines(iso_text, indent):
    lines = iso_text.splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(r"(async\s+)?def\s", l)), None)
    if start is None:
        return None
    out = []
    for l in lines[start + 1:]:
        out.append((" " * indent + l) if l.strip() else "")
    while out and not out[-1].strip():
        out.pop()
    return out


def splice(lines, pos, name, indent, body):
    pat = re.compile(r"^(\s*)(?:async\s+)?def\s+%s\s*\(" % re.escape(name))
    for i in range(pos, len(lines)):
        m = pat.match(lines[i])
        if not m or len(m.group(1)) != indent:
            continue
        j = i + 1
        while j < len(lines):
            s = lines[j]
            if not s.strip():
                j += 1; continue
            if len(s) - len(s.lstrip()) <= indent:
                break
            j += 1
        return lines[:i + 1] + body + lines[j:], i + 1 + len(body)
    return None, pos


def main():
    pyc, out = sys.argv[1], sys.argv[2]
    rep_path = sys.argv[sys.argv.index("--report") + 1] if "--report" in sys.argv else None
    root = load(pyc)
    objs = walk(root)
    skel = stub_children(root)
    text = run(skel)
    lines = text.splitlines()
    stubbed = [(n, c) for n, c in objs if n and not is_class(c) and c.co_name != "<module>"]
    pos, done, failed = 0, 0, []
    for name, code in stubbed:
        iso = isolate(code)
        # locate by name; indent unknown -> try all indents
        found = False
        for indent in (4, 8, 0, 12, 16, 20):
            body = body_lines(iso, indent)
            if body is None:
                continue
            new_lines, npos = splice(lines, pos, code.co_name, indent, body)
            if new_lines is not None:
                lines, pos = new_lines, npos
                done += 1; found = True
                break
        if not found:
            failed.append(name)
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    info = {"pyc": pyc, "objects": len(objs), "stubbed": len(stubbed),
            "spliced": done, "failed": failed}
    if rep_path:
        json.dump(info, open(rep_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in info.items() if k != "failed"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
