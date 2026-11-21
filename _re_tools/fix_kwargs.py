"""Rewrite pycdc's `f(a, b, **('k1', 'k2'))` back into `f(a, k1=b1, k2=b2)`."""
import ast
import io
import sys


def split_top(text):
    parts, depth, cur, quote = [], 0, [], None
    i = 0
    while i < len(text):
        ch = text[i]
        if quote:
            cur.append(ch)
            if ch == "\\":
                if i + 1 < len(text):
                    cur.append(text[i + 1])
                    i += 2
                    continue
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            cur.append(ch)
        elif ch in "([{":
            depth += 1
            cur.append(ch)
        elif ch in ")]}":
            depth -= 1
            cur.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
        i += 1
    parts.append("".join(cur))
    return parts


def fix(path):
    src = io.open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)
    offsets = [0]
    for ln in lines:
        offsets.append(offsets[-1] + len(ln))

    def pos(lineno, col):
        return offsets[lineno - 1] + col

    edits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.keywords:
            continue
        kw = node.keywords[-1]
        if kw.arg is not None:
            continue
        v = kw.value
        if not isinstance(v, (ast.Tuple, ast.List)):
            continue
        names = []
        ok = True
        for e in v.elts:
            if isinstance(e, ast.Constant) and isinstance(e.value, str):
                names.append(e.value)
            else:
                ok = False
        if not ok or not names:
            continue
        start = pos(node.func.end_lineno, node.func.end_col_offset)
        end = pos(node.end_lineno, node.end_col_offset)
        seg = src[start:end]
        if "**" not in seg:
            continue
        inner = seg[seg.index("(") + 1:seg.rindex(")")]
        items = [x for x in split_top(inner) if x.strip() != ""]
        star = items[-1].strip() if items else ""
        if not star.startswith("**"):
            print("SKIP %s:%d star" % (path, node.lineno))
            continue
        vals = items[-1 - len(names):-1]
        rest = items[:-1 - len(names)]
        if len(vals) != len(names):
            print("SKIP %s:%d count" % (path, node.lineno))
            continue
        new = [x.strip() for x in rest] + ["%s=%s" % (n, val.strip()) for n, val in zip(names, vals)]
        edits.append((start, end, "(" + ", ".join(new) + ")"))

    edits.sort(reverse=True)
    for start, end, repl in edits:
        src = src[:start] + repl + src[end:]
    io.open(path, "w", encoding="utf-8", newline="\n").write(src)
    return len(edits)


total = 0
for p in sys.argv[1:]:
    n = fix(p)
    print("%s: %d call(s)" % (p, n))
    total += n
print("total", total)
