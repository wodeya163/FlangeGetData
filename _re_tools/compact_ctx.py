import io, sys
p = "_re_tools/_ctx_ui.txt"
out = []
for ln in io.open(p, encoding="utf-8").read().splitlines():
    if ln.startswith(("_decompiled_tools", "  ")):
        # keep instruction lines; truncate long attr dump lines
        if len(ln) > 240:
            ln = ln[:240] + " ..."
        out.append(ln)
    else:
        out.append(ln)
io.open("_re_tools/_ctx_ui_small.txt", "w", encoding="utf-8", newline="\n").write("\n".join(out))
print(len(out))
