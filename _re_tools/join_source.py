"""Render a ``''.join([...])`` function body from bytecode.

pycdc often turns the list argument into an unreadable subscript chain.  This
helper only handles the regular list-append pattern used for QSS templates.
"""
from __future__ import annotations

import dis
import marshal
import sys
import types


def load(path: str) -> types.CodeType:
    return marshal.loads(open(path, "rb").read()[16:])


def walk(code: types.CodeType):
    yield code
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            yield from walk(const)


def find(path: str, name: str) -> types.CodeType:
    for code in walk(load(path)):
        if code.co_name == name:
            return code
    raise SystemExit("function not found: " + name)


def main() -> int:
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    code = find(sys.argv[1], sys.argv[2])
    mapping = sys.argv[3]
    ins = list(dis.get_instructions(code))
    pieces: list[str] = []
    i = 0
    while i < len(ins) - 4:
        # LOAD_CONST literal; LIST_APPEND
        if (ins[i].opname == "LOAD_CONST" and isinstance(ins[i].argval, str)
                and ins[i + 1].opname == "LIST_APPEND"):
            pieces.append(repr(ins[i].argval))
            i += 2
            continue
        # LOAD_FAST mapping; LOAD_CONST key; BINARY_SUBSCR; FORMAT_VALUE; LIST_APPEND
        if (ins[i].opname == "LOAD_FAST" and ins[i].argval == mapping
                and ins[i + 1].opname == "LOAD_CONST"
                and ins[i + 2].opname == "BINARY_SUBSCR"
                and ins[i + 3].opname == "FORMAT_VALUE"
                and ins[i + 4].opname == "LIST_APPEND"):
            key = ins[i + 1].argval
            pieces.append("f\"{%s[%r]}\"" % (mapping, key))
            i += 5
            continue
        # LOAD_FAST other; FORMAT_VALUE; LIST_APPEND
        if (ins[i].opname == "LOAD_FAST"
                and ins[i + 1].opname == "FORMAT_VALUE"
                and ins[i + 2].opname == "LIST_APPEND"):
            pieces.append("f\"{%s}\"" % ins[i].argval)
            i += 3
            continue
        i += 1
    if not pieces:
        raise SystemExit("recognized no join pieces")
    print("    return ''.join([")
    for piece in pieces:
        print("        " + piece + ",")
    print("    ])")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
