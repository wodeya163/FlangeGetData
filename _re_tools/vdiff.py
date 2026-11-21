"""Show the first bytecode difference between rebuilt source and original pyc."""
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


def main():
    src, pyc = sys.argv[1], sys.argv[2]
    want = sys.argv[3] if len(sys.argv) > 3 else None
    orig = dict(walk(load(pyc)))
    text = open(src, encoding="utf-8").read()
    new = {}
    # allow partial module: import-time errors are not expected, compile only
    mod = compile(text, src, "exec", dont_inherit=True)
    new = dict(walk(mod))
    if not want:
        for name, code in orig.items():
            if name not in new:
                print("MISSING", name)
                continue
            a, b = sig(code), sig(new[name])
            if [x[:2] for x in a] != [x[:2] for x in b]:
                i = next((k for k, (x, y) in enumerate(zip(a, b)) if x[:2] != y[:2]), min(len(a), len(b)))
                print("DIFF %-40s insn %d/%d  orig=%s new=%s" % (name, i, len(a), a[i][:2] if i < len(a) else None, b[i][:2] if i < len(b) else None))
        return
    code = orig[want]
    a, b = sig(code), sig(new[want])
    i = next((k for k, (x, y) in enumerate(zip(a, b)) if x[:2] != y[:2]), min(len(a), len(b)))
    print("### %s  %d vs %d instructions, first diff at %d" % (want, len(a), len(b), i))
    print("--- original ---")
    for k in range(max(0, i - 15), min(len(a), i + 16)):
        print("%s%5d %5d %-26s %s" % (">" if k == i else " ", k, a[k][2], a[k][0], a[k][1]))
    print("--- rebuilt ---")
    for k in range(max(0, i - 15), min(len(b), i + 16)):
        print("%s%5d %5d %-26s %s" % (">" if k == i else " ", k, b[k][2], b[k][0], b[k][1]))
    print("--- attrs ---")
    for attr in ("co_consts", "co_names", "co_varnames", "co_freevars", "co_cellvars"):
        x, y = getattr(code, attr), getattr(new[want], attr)
        if tuple(map(show, x)) != tuple(map(show, y)):
            print("%s:\n  orig=%s\n  new =%s" % (attr, [show(v) for v in x], [show(v) for v in y]))


main()
