"""Per-object decompilation with automatic re-assembly.

pycdc aborts a whole module as soon as one code object trips its stack
model, which silently truncates everything that follows.  This tool feeds
pycdc one code object at a time: children are replaced by stubs, the
container is decompiled, and each stub is then substituted with the real
child text.  Broken leaves are reported instead of being lost.

Run it with the interpreter matching the target bytecode version.

usage: split_decompile.py <module.pyc> <out.py> [--report report.json]
"""
from __future__ import annotations

import importlib.util
import ast
import json
import marshal
import os
import re
import subprocess
import sys
import tempfile
import types

PYCDC = os.environ.get("PYCDC") or r"C:\Users\Administrator\AppData\Local\Temp\pycdc-shak2-build\pycdc.exe"
MAGIC = importlib.util.MAGIC_NUMBER
V311 = sys.version_info >= (3, 11)
LINEATTR = 'co_linetable' if hasattr(compile('pass', '<t>', 'exec'), 'co_linetable') else 'co_lnotab'
HEADER_LINES = 4

DUMMY_FUNC = compile("def _f():\n    pass\n", "<stub>", "exec").co_consts[0]
DUMMY_CLASS_MOD = compile("class _C:\n    pass\n", "<stub>", "exec")


def pyc_bytes(code: types.CodeType) -> bytes:
    return MAGIC + b"\x00" * 4 + b"\x00" * 8 + marshal.dumps(code)


def rebuild(code: types.CodeType, **kw) -> types.CodeType:
    """CodeType.replace that tolerates fields missing on older versions."""
    fields = {"co_argcount", "co_posonlyargcount", "co_kwonlyargcount",
              "co_nlocals", "co_stacksize", "co_flags", "co_code",
              "co_consts", "co_names", "co_varnames", "co_filename",
              "co_name", "co_qualname", "co_firstlineno", "co_linetable",
              "co_lnotab", "co_exceptiontable", "co_freevars", "co_cellvars"}
    kw = {k: v for k, v in kw.items() if k in fields and hasattr(code, k)}
    try:
        return code.replace(**kw)
    except TypeError:
        return types.CodeType(
            code.co_argcount, code.co_posonlyargcount, code.co_kwonlyargcount,
            code.co_nlocals, code.co_stacksize, code.co_flags, code.co_code,
            code.co_consts, code.co_names, code.co_varnames, code.co_filename,
            code.co_name, code.co_qualname, code.co_firstlineno,
            code.co_linetable, code.co_exceptiontable, code.co_freevars,
            code.co_cellvars)


def is_class_body(code: types.CodeType) -> bool:
    return ("__qualname__" in code.co_names
            and "__module__" in code.co_names
            and code.co_name != "<module>")


def is_def_child(code: types.CodeType) -> bool:
    """True for nested objects that appear as a def/class, not a comprehension."""
    return not code.co_name.startswith("<")


def stub_func(code: types.CodeType) -> types.CodeType:
    kw = dict(co_code=DUMMY_FUNC.co_code, co_consts=(None,), co_names=(),
              co_stacksize=2)
    kw[LINEATTR] = getattr(DUMMY_FUNC, LINEATTR)
    if hasattr(code, "co_exceptiontable"):
        kw["co_exceptiontable"] = b""
    return rebuild(code, **kw)


def stub_class(code: types.CodeType) -> types.CodeType:
    body = DUMMY_CLASS_MOD.co_consts[0]
    kw = dict(co_code=body.co_code, co_consts=body.co_consts,
              co_names=body.co_names, co_stacksize=2)
    kw[LINEATTR] = getattr(body, LINEATTR)
    if hasattr(code, "co_exceptiontable"):
        kw["co_exceptiontable"] = b""
    return rebuild(code, **kw)


def run_pycdc(code: types.CodeType, tag: str, tmp: str) -> tuple[str, int]:
    path = os.path.join(tmp, tag + ".pyc")
    with open(path, "wb") as fh:
        fh.write(pyc_bytes(code))
    try:
        res = subprocess.run([PYCDC, path], capture_output=True, timeout=45)
    except subprocess.TimeoutExpired:
        return "", 124
    return res.stdout.decode("utf-8", "replace"), res.returncode


def strip_header(text: str) -> str:
    lines = text.splitlines()
    while lines and (lines[0].startswith("#") or not lines[0].strip()):
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def build_wrapper(kind: str, name: str, body: types.CodeType) -> types.CodeType:
    if kind == "class":
        src = "class %s:\n    pass\n" % name
        mod = compile(src, "<stub>", "exec")
        inner = [c for c in mod.co_consts if isinstance(c, types.CodeType)][0]
        consts = tuple(body if c is inner else c for c in mod.co_consts)
        return mod.replace(co_consts=consts)
    src = "def %s():\n    pass\n" % name
    mod = compile(src, "<stub>", "exec")
    inner = [c for c in mod.co_consts if isinstance(c, types.CodeType)][0]
    consts = tuple(body if c is inner else c for c in mod.co_consts)
    return mod.replace(co_consts=consts)


def indent(text: str, pad: str) -> str:
    return "\n".join((pad + ln) if ln.strip() else "" for ln in text.splitlines())


def replace_block(text: str, name: str, new: str, report: dict, path: str) -> str:
    pat = re.compile(r"^(?P<ind>[ \t]*)(?:def|class)\s+" + re.escape(name) + r"\b",
                     re.M)
    m = pat.search(text)
    if not m:
        report["unplaced"].append(name)
        return text
    ind = m.group("ind")
    start = text.rfind("\n", 0, m.start()) + 1
    end = start
    for ln in text[start:].splitlines(True):
        end += len(ln)
        if end == start + len(ln):
            continue  # the def/class line itself
        if not ln.strip():
            continue
        cur = len(ln) - len(ln.lstrip(" \t"))
        if cur <= len(ind):
            end -= len(ln)
            break
    body = indent(new, ind)
    return text[:start] + body + "\n" + text[end:]


def render(code: types.CodeType, kind: str, name: str, depth: int,
           tmp: str, report: dict, trail: str) -> str | None:
    children = [c for c in code.co_consts
                if isinstance(c, types.CodeType) and is_def_child(c)]
    stubbed = code
    if children:
        stubbed = rebuild(code, co_consts=tuple(
            (stub_class(k) if is_class_body(k) else stub_func(k))
            if isinstance(k, types.CodeType) and is_def_child(k) else k
            for k in code.co_consts))

    if kind == "module":
        text, rc = run_pycdc(stubbed, "m" + str(depth), tmp)
    else:
        text, rc = run_pycdc(build_wrapper(kind, name, stubbed),
                             "w" + str(depth), tmp)
    text = strip_header(text)
    if rc != 0 or not text.strip():
        report["failed"].append(trail)
        return None
    if kind != "module":
        first = text.splitlines()[0]
        if not re.match(r"\s*(?:async\s+)?(?:def|class)\s+" + re.escape(name) + r"\b",
                        first):
            report["failed"].append(trail + " (bad-head)")
            return None

    for child in children:
        ckind = "class" if is_class_body(child) else "func"
        sub = render(child, ckind, child.co_name, depth + 1, tmp, report,
                     trail + "." + child.co_name)
        if sub is None:
            continue
        text = replace_block(text, child.co_name, sub, report, trail)
    if kind != "module":
        try:
            ast.parse(text)
        except SyntaxError:
            report["broken"].append(trail)
    return text


def main() -> int:
    pyc, out = sys.argv[1], sys.argv[2]
    report_path = None
    if "--report" in sys.argv:
        report_path = sys.argv[sys.argv.index("--report") + 1]
    root = marshal.loads(open(pyc, "rb").read()[16:])
    report = {"failed": [], "unplaced": [], "broken": []}
    with tempfile.TemporaryDirectory() as tmp:
        text = render(root, "module", "<module>", 0, tmp, report, "<module>")
    if text is None:
        print("module itself failed", file=sys.stderr)
        return 2
    head = ("# Reconstructed from bytecode by split_decompile.py\n"
            "# %s\n\n" % os.path.basename(pyc))
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(head + text + "\n")
    if report_path:
        with open(report_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=2)
    bad = sorted(set(report["failed"]))
    print("failed objects: %d" % len(bad))
    for b in bad:
        print("  " + b)
    broken = sorted(set(report["broken"]))
    if broken:
        print("syntactically broken objects: %d" % len(broken))
        for b in broken:
            print("  " + b)
    if report["unplaced"]:
        print("unplaced: " + ", ".join(sorted(set(report["unplaced"]))))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
