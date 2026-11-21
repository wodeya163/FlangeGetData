import sys, io
path = sys.argv[1]
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 60
marked = []
for _ in range(limit):
    src = open(path, encoding="utf-8").read()
    try:
        compile(src, path, "exec")
        break
    except SyntaxError as e:
        ln = e.lineno
        lines = src.splitlines()
        if not ln or ln > len(lines):
            print("cannot locate error:", e.msg); break
        raw = lines[ln - 1]
        if raw.strip().startswith("#"):
            print("already comment, stop:", ln, e.msg); break
        indent = raw[:len(raw) - len(raw.lstrip())]
        lines[ln - 1] = indent + "pass  # [反编译] 此行无法还原，需人工核对：" + raw.strip()[:60]
        marked.append(ln)
        open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
else:
    print("limit reached")
print("marked lines:", len(marked), marked[:20])
