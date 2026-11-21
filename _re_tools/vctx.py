"""Compact per-object first-diff context for all differing code objects."""
import dis, marshal, sys, types


def load(path):
    return marshal.loads(open(path, "rb").read()[16:])


def walk(code, prefix=""):
    name = prefix + (code.co_name if code.co_name != "<module>" else "")
    yield name, code
    for c in code.co_consts:
        if isinstance(c, types.CodeType):
            yield from walk(c, name + "." if name else "")


def show(arg):
    if isinstance(arg, types.CodeType):
        return "<code %s>" % arg.co_name
    if isinstance(arg, (set, frozenset)):
        return "{%s}" % ", ".join(sorted(show(x) for x in arg))
    if isinstance(arg, (list, tuple)):
        inner = ", ".join(show(x) for x in arg)
        return "[%s]" % inner if isinstance(arg, list) else ("(%s,)" % inner if len(arg) == 1 else "(%s)" % inner)
    return repr(arg)


def sig(code):
    return [(i.opname, show(i.argval), i.offset) for i in dis.get_instructions(code)]


src, pyc = sys.argv[1], sys.argv[2]
wide = int(sys.argv[3]) if len(sys.argv) > 3 else 8
orig = dict(walk(load(pyc)))
mod = compile(open(src, encoding="utf-8").read(), src, "exec", dont_inherit=True)
new = dict(walk(mod))
for name, code in orig.items():
    if name not in new:
        print("===== MISSING %s" % name)
        continue
    a, b = sig(code), sig(new[name])
    if [x[:2] for x in a] == [x[:2] for x in b]:
        continue
    i = next((k for k, (x, y) in enumerate(zip(a, b)) if x[:2] != y[:2]), min(len(a), len(b)))
    print("===== %s   (%d vs %d insns, first diff %d)" % (name, len(a), len(b), i))
    for k in range(max(0, i - wide), min(len(a), i + wide + 1)):
        print("  O %s%5d %5d %-24s %s" % (">" if k == i else " ", k, a[k][2], a[k][0], a[k][1]))
    for k in range(max(0, i - wide), min(len(b), i + wide + 1)):
        print("  N %s%5d %5d %-24s %s" % (">" if k == i else " ", k, b[k][2], b[k][0], b[k][1]))
    for attr in ("co_consts", "co_names", "co_varnames", "co_freevars", "co_cellvars"):
        x, y = getattr(code, attr), getattr(new[name], attr)
        if tuple(map(show, x)) != tuple(map(show, y)):
            print("  %s O=%s" % (attr, [show(v) for v in x]))
            print("  %s N=%s" % (" " * len(attr), [show(v) for v in y]))
