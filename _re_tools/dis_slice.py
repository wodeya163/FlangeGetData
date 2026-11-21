"""Print one [Code] block from pycdas output for a .pyc file.

usage: dis_slice.py <module.pyc> <object name|substring> [max_lines]
"""
from __future__ import annotations

import re
import subprocess
import sys

PYCDAS = r"C:\Users\Administrator\AppData\Local\Temp\pycdc-shak2-build\pycdas.exe"


def main() -> int:
    pyc, name = sys.argv[1], sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    out = subprocess.run([PYCDAS, pyc], capture_output=True, text=True,
                         encoding="utf-8", errors="replace").stdout
    lines = out.splitlines()
    starts = [i for i, ln in enumerate(lines) if ln.strip().startswith("Object Name:")]
    for idx, i in enumerate(starts):
        obj = lines[i].split("Object Name:", 1)[1].strip()
        if name != obj and name not in obj:
            continue
        end = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        block = lines[i - 1:end]
        print("\n".join(block[:limit]))
        print(f"--- {len(block)} lines total ---")
        return 0
    print(f"no object matching {name!r}; objects: "
          + ", ".join(lines[i].split('Object Name:', 1)[1].strip() for i in starts))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
