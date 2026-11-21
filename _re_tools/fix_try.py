import re, sys
path = sys.argv[1]
lines = open(path, encoding="utf-8").read().splitlines()
out, fixed = [], []
i = 0
while i < len(lines):
    l = lines[i]
    out.append(l)
    m = re.match(r"^(\s*)try:\s*$", l)
    if m:
        ind = len(m.group(1))
        j = i + 1
        body = []
        while j < len(lines):
            s = lines[j]
            if s.strip() and (len(s) - len(s.lstrip())) <= ind:
                break
            body.append(s); j += 1
        nxt = lines[j].strip() if j < len(lines) else ""
        if not re.match(r"^(except|finally)\b", nxt):
            out.append(" " * (ind + 4) + "pass")
            out.append(" " * ind + "except Exception:")
            out.append(" " * (ind + 4) + "pass  # [反编译] 原异常处理分支未能还原")
            fixed.append(i + 1)
            i = j
            continue
    i += 1
open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
print("patched try blocks:", len(fixed), fixed[:10])
