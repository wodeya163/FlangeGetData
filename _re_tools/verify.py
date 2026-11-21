"""Compare rebuilt source against the original bytecode, function by function.

Run with the interpreter matching the target version, e.g.
    py3.11.9\\python.exe verify.py module.py module.pyc [--verbose]

Exit code 0 means every code object matched instruction-for-instruction.
"""
from __future__ import annotations

import argparse
import dis
import marshal
import sys
import types


def load_pyc(path: str) -> types.CodeType:
    return marshal.loads(open(path, "rb").read()[16:])


def walk(code: types.CodeType, prefix: str = ""):
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


def signature(code: types.CodeType, lenient: bool = False):
    all_ins = list(dis.get_instructions(code))

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

    if not lenient:
        return [(ins.opname, show(ins.argval)) for ins in all_ins]

    forward = {}
    for k, ins in enumerate(all_ins):
        if ins.opcode in dis.hasjrel or ins.opcode in dis.hasjabs:
            forward[ins.offset] = ins.argval
        elif k + 1 < len(all_ins):
            forward[ins.offset] = all_ins[k + 1].offset

    kept = [ins for ins in all_ins
            if ins.opname not in ("NOP", "JUMP_FORWARD", "EXTENDED_ARG")]
    survivors = {ins.offset: k for k, ins in enumerate(kept)}

    out = []
    for k, ins in enumerate(kept):
        arg = ins.argval
        opname = ins.opname
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("pyc")
    ap.add_argument("--verbose", "-v", action="store_true")
    ap.add_argument("--quiet", "-q", action="store_true")
    ap.add_argument("--lenient", "-l", action="store_true")
    args = ap.parse_args()

    orig = dict(walk(load_pyc(args.pyc)))
    text = open(args.source, encoding="utf-8").read()
    rebuilt = compile(text, args.source, "exec", dont_inherit=True)
    new = dict(walk(rebuilt))

    missing = [n for n in orig if n not in new]
    extra = [n for n in new if n not in orig]
    same, differ = [], []
    for name, code in orig.items():
        if name not in new:
            continue
        a, b = signature(code, args.lenient), signature(new[name], args.lenient)
        d = first_diff(a, b)
        if d is None:
            same.append(name)
        else:
            differ.append((name, d, len(a), len(b)))

    total = len(orig)
    if not args.quiet:
        print("objects: %d  exact: %d  differ: %d  missing: %d  extra: %d"
              % (total, len(same), len(differ), len(missing), len(extra)))
        for name, d, la, lb in differ:
            i, x, y = d
            print("  DIFF %-45s insn %d/%d  orig=%s  new=%s"
                  % (name, i, la, x, y))
            if args.verbose:
                print("       (new has %d insns, orig %d)" % (lb, la))
        for name in missing:
            print("  MISSING %s" % name)
        for name in extra:
            print("  EXTRA %s" % name)
    return 0 if not differ and not missing and not extra else 1


if __name__ == "__main__":
    raise SystemExit(main())
