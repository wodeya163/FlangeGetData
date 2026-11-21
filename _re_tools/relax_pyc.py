"""Rewrite branch-or-pop opcodes into plain conditional jumps.

pycdc's stack model breaks on ``JUMP_IF_*_OR_POP`` (Python 3.11) and aborts
the whole module.  Both opcode pairs have the same size and operand
encoding, so swapping them keeps every jump target valid.  The rewritten
pyc is only used as decompiler input; verification always runs against the
original bytecode, so the affected ``and``/``or`` lines are re-checked and
restored by hand.

usage: relax_pyc.py <src.pyc> <dst.pyc>
"""
from __future__ import annotations

import dis
import importlib.util
import marshal
import sys
import types

MAGIC = importlib.util.MAGIC_NUMBER
SWAPS = {
    dis.opmap["JUMP_IF_TRUE_OR_POP"]: dis.opmap["POP_JUMP_FORWARD_IF_TRUE"],
    dis.opmap["JUMP_IF_FALSE_OR_POP"]: dis.opmap["POP_JUMP_FORWARD_IF_FALSE"],
}


def relax(code: types.CodeType) -> types.CodeType:
    raw = bytearray(code.co_code)
    for offset in range(0, len(raw), 2):
        new = SWAPS.get(raw[offset])
        if new is not None:
            raw[offset] = new
    consts = tuple(relax(item) if isinstance(item, types.CodeType) else item
                   for item in code.co_consts)
    return code.replace(co_code=bytes(raw), co_consts=consts)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    with open(sys.argv[1], "rb") as handle:
        data = handle.read()
    code = marshal.loads(data[16:])
    with open(sys.argv[2], "wb") as handle:
        handle.write(MAGIC + b"\x00" * 12 + marshal.dumps(relax(code)))
    print("relaxed ->", sys.argv[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
