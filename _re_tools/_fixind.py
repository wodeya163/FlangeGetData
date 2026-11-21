import io
p=r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py"
s=io.open(p,encoding="utf-8").read().splitlines(True)
start=None; end=None
for n,l in enumerate(s):
    if l=="            rng = compression_range(d2, seal_type)\n": start=n
for n,l in enumerate(s):
    if l.startswith("class GrooveTab"): end=n; break
print("start",start,"end",end)
assert start is not None and end is not None and start<end
for k in range(start+1,end):
    if s[k].strip():
        s[k]="    "+s[k]
out="".join(s)
out=out.replace("""    def set_gap(self, gap_mm):
        if not gap_mm:
            pass
        self.gap = 0.0
        self.update()
""","""    def set_gap(self, gap_mm):
        self.gap = gap_mm or 0.0
        self.update()
""")
io.open(p,"w",encoding="utf-8",newline="\n").write(out)
print("ok")
