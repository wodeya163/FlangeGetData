"""Load a .pyc (16-byte header) and disassemble one code object by name."""
from __future__ import annotations

import dis
import io
import marshal
import sys
import types


def load(path: str) -> types.CodeType:
    data = open(path, "rb").read()
    return marshal.loads(data[16:])


def walk(code: types.CodeType):
    yield code
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            yield from walk(const)


def find(code: types.CodeType, needle: str) -> list[types.CodeType]:
    out = []
    for c in walk(code):
        qual = getattr(c, "co_qualname", c.co_name)
        if c.co_name == needle or needle in qual:
            out.append(c)
    return out


def dump(path: str, needle: str) -> int:
    root = load(path)
    matches = find(root, needle)
    if not matches:
        print(f"no match for {needle!r}")
        return 1
    for c in matches:
        qual = getattr(c, "co_qualname", c.co_name)
        print(f"### {qual}  firstlineno={c.co_firstlineno} "
              f"args={c.co_varnames[:c.co_argcount]} "
              f"vars={c.co_varnames[c.co_argcount:c.co_argcount + c.co_nlocals]}")
        dis.dis(c)
        print()
    return 0


def listing(path: str) -> int:
    for c in walk(load(path)):
        qual = getattr(c, "co_qualname", c.co_name)
        print(f"{c.co_firstlineno:5d}  {qual}  ({len(c.co_code)} bytes)")
    return 0


if __name__ == "__main__":
    mode, path = sys.argv[1], sys.argv[2]
    if mode == "list":
        raise SystemExit(listing(path))
    raise SystemExit(dump(path, sys.argv[3]))
