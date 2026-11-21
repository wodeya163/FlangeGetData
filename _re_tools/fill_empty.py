import re, sys
path = sys.argv[1]
lines = open(path, encoding="utf-8").read().splitlines()
out, filled = [], []
i = 0
while i < len(lines):
    l = lines[i]
    out.append(l)
    m = re.match(r"^(\s*)(?:async\s+)?(def|class)\s+([\w\.<>]+)", l)
    if m:
        indent = len(m.group(1))
        j = i + 1
        has = False
        while j < len(lines):
            s = lines[j]
            if not s.strip():
                j += 1
                continue
            if len(s) - len(s.lstrip()) <= indent:
                break
            has = True
            break
        if not has:
            out.append(" " * (indent + 4) + "pass  # body not recovered")
            filled.append(m.group(3))
    i += 1
open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("filled", len(filled), filled[:12])
