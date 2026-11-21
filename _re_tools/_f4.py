import io
p=r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py"
s=io.open(p,encoding="utf-8").read()
pairs=[
("        w = self.width()\n        h = self.height()\n","        w, h = self.width(), self.height()\n"),
("        g = None.groove\n","        g = self.groove\n"),
("        if p_mpa is not None:\n            pass\n        pressurized = not (p_mpa <= 0)\n","        pressurized = not (p_mpa is None or p_mpa <= 0)\n"),
("        scale_h = (h * 0.84 - y0) / (h_mm + gap_mm if gap_mm > 0 else 0)\n","        scale_h = (h * 0.84 - y0) / (h_mm + (gap_mm if gap_mm > 0 else 0))\n"),
("        gap_draw = max(gap_px, 3) if gap_mm > 0 else 0\n","        gap_draw = max(gap_px, 3.0) if gap_mm > 0 else 0\n"),
]
for a,b in pairs:
    assert a in s,a
    s=s.replace(a,b)
io.open(p,"w",encoding="utf-8",newline="\n").write(s)
print("ok")
