import os, sys, dis, marshal, types

def load_pyc(path):
    data = open(path, "rb").read()
    return marshal.loads(data[16:])

def walk(code, prefix=""):
    name = prefix + (code.co_name if code.co_name != "<module>" else "")
    yield name, code
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            yield from walk(const, name + "." if name else "")

def _resolve(offset, survivors, forward):
    seen = set()
    while offset not in survivors:
        if offset in seen:
            return None
        seen.add(offset)
        offset = forward.get(offset)
        if offset is None:
            return None
    return survivors[offset]

def signature(code, lenient=True):
    ins_all = list(dis.get_instructions(code))
    def show(arg):
        if isinstance(arg, types.CodeType):
            return "<code %s>" % arg.co_name
        if isinstance(arg, (set, frozenset)):
            return "{%s}" % ", ".join(sorted(show(x) for x in arg))
        if isinstance(arg, (list, tuple)):
            inner = ", ".join(show(x) for x in arg)
            if isinstance(arg, list):
                return "[%s]" % inner
            return "(%s,)" % inner if len(arg) == 1 else "(%s)" % inner
        if lenient and not isinstance(arg, bool) and isinstance(arg, (int, float)):
            return "num(%r)" % float(arg)
        return repr(arg)
    forward = {}
    for k, ins in enumerate(ins_all):
        if ins.opcode in dis.hasjrel or ins.opcode in dis.hasjabs:
            forward[ins.offset] = ins.argval
        elif k + 1 < len(ins_all):
            forward[ins.offset] = ins_all[k + 1].offset
    kept = [i for i in ins_all if i.opname not in ("NOP", "JUMP_FORWARD", "EXTENDED_ARG")]
    survivors = {i.offset: k for k, i in enumerate(kept)}
    out = []
    for k, ins in enumerate(kept):
        arg, opname = ins.argval, ins.opname
        if (opname in ("LOAD_METHOD", "LOAD_ATTR") and k + 1 < len(kept)
                and kept[k + 1].opname == "PRECALL"):
            opname = "LOAD_CALLABLE"
        if ins.opcode in dis.hasjrel or ins.opcode in dis.hasjabs:
            tgt = _resolve(arg, survivors, forward)
            arg = "->%s" % ("?" if tgt is None else tgt)
        else:
            arg = show(arg)
        out.append((opname, arg))
    return out

def first_diff(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i, x, y
    if len(a) != len(b):
        i = min(len(a), len(b))
        return i, (a[i] if i < len(a) else None), (b[i] if i < len(b) else None)
    return None

app = sys.argv[1]
base = os.path.join("_decompiled_tools", app)
src_root = os.path.join(base, "source")
pyc_root = os.path.join(base, "original_pyc")
rows = []
for dirpath, _, files in os.walk(src_root):
    if "__pycache__" in dirpath:
        continue
    for f in sorted(files):
        if not f.endswith(".py"):
            continue
        src = os.path.join(dirpath, f)
        rel = os.path.relpath(src, src_root)
        pyc = os.path.join(pyc_root, rel[:-3] + ".pyc")
        if not os.path.exists(pyc):
            rows.append((rel, "NOPYC", "-", "-", "-", ""))
            continue
        try:
            orig = dict(walk(load_pyc(pyc)))
            text = open(src, encoding="utf-8").read()
            try:
                new = dict(walk(compile(text, src, "exec", dont_inherit=True)))
            except SyntaxError as e:
                rows.append((rel, "SYNTAX", "-", "-", "-", "line %s" % e.lineno))
                continue
        except Exception as e:
            rows.append((rel, "LOADERR", "-", "-", "-", str(e)[:60]))
            continue
        missing = [n for n in orig if n not in new]
        extra = [n for n in new if n not in orig]
        differ = []
        for name, code in orig.items():
            if name not in new:
                continue
            a, b = signature(code), signature(new[name])
            d = first_diff(a, b)
            if d is not None:
                differ.append((name, d[0], len(a), len(b), d[1], d[2]))
        status = "EXACT" if not missing and not extra and not differ else "DIFF"
        detail = ""
        if differ:
            n, i, la, lb, x, y = differ[0]
            detail = "%s @%d/%d" % (n, i, la)
        rows.append((rel, status, len(orig), len(differ), len(missing), detail + (" extra=%d" % len(extra) if extra else "")))

bad = [r for r in rows if r[1] not in ("EXACT",)]
for r in rows:
    print("%-38s %-7s obj=%-4s diff=%-3s miss=%-3s %s" % r)
print("---- %d files, %d problems" % (len(rows), len(bad)))
