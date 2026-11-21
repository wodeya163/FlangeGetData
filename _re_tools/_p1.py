p=r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py"
s=open(p,encoding="utf-8-sig").read()
def rep(a,b):
    global s
    assert a in s, a[:60]
    s=s.replace(a,b,1)
rep("""    if None in ('hydraulic_dynamic', 'dynamic_recip', 'pneumatic_dynamic'):""",
    """    if seal_type in ('hydraulic_dynamic', 'dynamic_recip', 'pneumatic_dynamic'):""")
rep("""    if None == 'dynamic_rotate':""","""    if seal_type == 'dynamic_rotate':""")
rep("""        if out["ok"]:
            head = f"{name}：自填 {v:.2f} mm ✓ 在{lim['formula']}界限（{sym}{limit:.2f}）内，公差 H11"
        else:
            head = f"{name}：自填 {v:.2f} mm ⚠ 超出{lim['formula']}上限 {limit:.2f} mm，公差 H11"
""","""        head = f"{name}：自填 {v:.2f} mm ✓ 在{lim['formula']}界限（{sym}{limit:.2f}）内，公差 H11" if out["ok"] else f"{name}：自填 {v:.2f} mm ⚠ 超出{lim['formula']}上限 {limit:.2f} mm，公差 H11"
""")
rep("""        if out["ok"]:
            head = f"{name}：自填 {v:.2f} mm ✓ 在{lim['formula']}界限（{sym}{limit:.2f}）内，公差 H11"
        else:
            head = f"{name}：自填 {v:.2f} mm ⚠ 低于{lim['formula']}下限 {limit:.2f} mm，公差 H11"
""","""        head = f"{name}：自填 {v:.2f} mm ✓ 在{lim['formula']}界限（{sym}{limit:.2f}）内，公差 H11" if out["ok"] else f"{name}：自填 {v:.2f} mm ⚠ 低于{lim['formula']}下限 {limit:.2f} mm，公差 H11"
""")
rep("""BG_H = None
CARD_H = None
ACCENT_H = None""","""BG_H = CARD_H = None
ACCENT_H = None""")
rep("""    if not t:
        pass
    t = theme.current()""","""    t = t or theme.current()""")
open(p,"w",encoding="utf-8",newline="").write(s)
print("ok")
