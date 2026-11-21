import io

BASE = "_decompiled_tools/密封圈选型工具V2.5/source/"


def rd(p):
    return io.open(BASE + p, encoding="utf-8").read()


def wr(p, s):
    io.open(BASE + p, "w", encoding="utf-8", newline="\n").write(s)


def cut(text, start, end):
    i = text.index(start)
    j = text.index(end, i)
    return text[:i], text[i:j], text[j:]


# ---------------- seal_data ----------------
sd = rd("seal_data.py")
old = ("ORING_SIZES = (lambda .0: for None in .0:\n"
       "(lo, hi) = (d2,)None[None])(_D2_RANGES.items())")
new = ("ORING_SIZES = {d2: [v for v in _D1_ROWS if lo <= v <= hi]\n"
       "               for d2, (lo, hi) in _D2_RANGES.items()}")
assert old in sd
sd = sd.replace(old, new)

head, body, tail = cut(sd, "def recommend_material_ex(", "\ndef recommend_backup_ring(")
body = '''def recommend_material_ex(medium, temp_min, temp_max):
    \'\'\'按介质评级与温度筛选材料，返回 (推荐列表[(code, reason)], 排除列表[(code, why)])。

    评级等级：优 > 良 > 可 > 劣 > -，只保留「良」及以上。
    temp_min/temp_max 为 None 时视为不限温度。
    \'\'\'
    mkey = _MEDIA_RATE_KEY.get(medium, "").strip()
    ok, excluded = [], []
    for code, m in MATERIALS.items():
        lo, hi = m["temp"]
        if temp_min is None or temp_max is None:
            temp_ok, temp_part = True, f"温度{lo}~{hi}℃"
        elif temp_min >= lo and temp_max <= hi:
            temp_ok, temp_part = True, f"温度{lo}~{hi}℃覆盖工况"
        else:
            temp_ok, temp_part = False, ""
        if not temp_ok:
            if temp_min < lo:
                why = f"温度不符：长期工作温度{lo}~{hi}℃，工况最低{temp_min:.0f}℃低于下限{lo}℃（手册表3-3-2/3-3-3 原文值）"
            else:
                why = f"温度不符：长期工作温度{lo}~{hi}℃，工况最高{temp_max:.0f}℃高于上限{hi}℃（手册表3-3-2/3-3-3 原文值）"
            excluded.append((code, why))
            continue
        if mkey:
            rkey, rlabel = mkey
            rating = m["rates"].get(rkey, "-")
            rank = _RATE_RANK.get(rating, 0)
            if rank < 2:
                excluded.append((code, f"介质不符：{rlabel}评级「{rating}」，不适合该介质"))
                continue
            reason = f"{rlabel} {rating}；{temp_part}"
            score = (rank, hi - max(temp_max or hi, lo))
        else:
            reason = f"手册表未收录该介质评级，按温度筛选（{temp_part}）"
            score = (0, hi - max(temp_max or hi, lo))
        ok.append((code, reason, score))
    ok.sort(key=lambda x: -x[2][0] * 1000 - x[2][1])
    return [(code, reason) for code, reason, _ in ok], excluded
'''
sd = head + body + tail
wr("seal_data.py", sd)

# ---------------- seal_ui ----------------
su = rd("seal_ui.py")
head, body, tail = cut(su, "def axial_row_info(", "\nBG = ")
body = '''def axial_row_info(d1, d2, dir_key, user_text):
    \'\'\'轴向密封沟槽直径 d7/d8 的展示信息（GB/T 3452.3-2005 式(3)/(4)，公差表3 H11）。

    标准表12/表13 推荐值本工具未收录（2026-10-22 定）：界面留「—」并支持用户自填实际值。
    返回 dict(label, hint, gi, filled, ok) 或 None（非轴向）：
      label  — 输入框标签（沟槽外径 d7 / 沟槽内径 d8）
      hint   — 界限与出处短句
      gi     — 结果区追加行（list[str]，可能为空）
      filled — 用户是否填了值
      ok     — True 在界限内 / False 超出界限 / None 未填或无法判定
    \'\'\'
    if dir_key not in ("internal", "external"):
        return None
    internal = dir_key == "internal"
    label = "沟槽外径 d7 (mm)：" if internal else "沟槽内径 d8 (mm)："
    lim = axial_diameter_limits(d1, d2, dir_key)
    if lim.get("undefined"):
        return {"label": label,
                "hint": "需要 O 型圈内径 d1 才能给出界限值",
                "gi": [], "filled": False, "ok": None}
    limit = lim["limit"]
    sym = "≤" if internal else "≥"
    table_no = "表12" if internal else "表13"
    hint = f"{sym}{limit:.2f} mm（{lim['formula']}，公差 H11）；标准{table_no}推荐值未收录，可自填"
    out = {"label": label, "hint": hint, "gi": [], "filled": False, "ok": None}
    txt = (user_text or "").strip()
    if not txt:
        out["gi"].append(f"{lim['label']}：界限 {sym}{limit:.2f} mm（{lim['formula']}，公差 H11）；标准{table_no}推荐值未收录，未自填")
        return out
    try:
        v = float(txt)
    except ValueError:
        out["gi"].append(f"{lim['label']}：自填值「{txt}」不是数字，未参与计算")
        return out
    out["filled"] = True
    name = lim["label"]
    if internal:
        out["ok"] = v <= limit
        if out["ok"]:
            head = f"{name}：自填 {v:.2f} mm ✓ 在{lim['formula']}界限（{sym}{limit:.2f}）内，公差 H11"
        else:
            head = f"{name}：自填 {v:.2f} mm ⚠ 超出{lim['formula']}上限 {limit:.2f} mm，公差 H11"
    else:
        out["ok"] = v >= limit
        if out["ok"]:
            head = f"{name}：自填 {v:.2f} mm ✓ 在{lim['formula']}界限（{sym}{limit:.2f}）内，公差 H11"
        else:
            head = f"{name}：自填 {v:.2f} mm ⚠ 低于{lim['formula']}下限 {limit:.2f} mm，公差 H11"
    out["gi"].append(head)
    return out

'''
su = head + body + tail

head, body, tail = cut(su, "def _bg_lum(", "\n_SECTION_DARK = ")
body = '''def _bg_lum(hexs):
    \'\'\'背景亮度（WCAG 相对亮度），用于截面图调色板明暗切换。\'\'\'
    hexs = hexs.lstrip("#")
    (r, g, b) = (int(hexs[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
'''
su = head + body + tail
wr("seal_ui.py", su)

# ---------------- theme ----------------
th = rd("theme.py")
head, body, tail = cut(th, "def _arrow_pngs(", "\ndef qss(")
body = '''def _arrow_pngs(color_hex):
    \'\'\'按给定颜色生成（或复用）上/下三角箭头 PNG，返回 (up路径, down路径)。\'\'\'
    import hashlib
    import tempfile
    from PySide6.QtCore import QPointF, QSize
    from PySide6.QtGui import QColor, QPainter, QPixmap, QPolygonF
    up_poly = [(5, 1), (9, 8), (1, 8)]
    dn_poly = [(5, 8), (9, 2), (1, 2)]
    key = hashlib.md5((color_hex + repr((up_poly, dn_poly))).encode("utf-8")).hexdigest()[:8]
    d = os.path.join(tempfile.gettempdir(), "sealtool_arrows")
    os.makedirs(d, exist_ok=True)
    up_p = os.path.join(d, f"up_{key}.png").replace("\\\\", "/")
    dn_p = os.path.join(d, f"dn_{key}.png").replace("\\\\", "/")
    if not os.path.exists(up_p) or not os.path.exists(dn_p):
        for path, poly in ((up_p, up_poly), (dn_p, dn_poly)):
            pm = QPixmap(QSize(10, 10))
            pm.fill(Qt.transparent)
            p = QPainter(pm)
            p.setRenderHint(QPainter.Antialiasing)
            p.setBrush(QColor(color_hex))
            p.setPen(Qt.NoPen)
            p.drawPolygon(QPolygonF([QPointF(*pt) for pt in poly]))
            p.end()
            pm.save(path)
    return (up_p, dn_p)
'''
th = head + body + tail

old = '''        c = (lambda .0 = None: [ int(h[i:i + 2], 16) / 255 for i in .0 ])((0, 2, 4))
        c = (lambda .0: for x in .0:
    passcontinuex / 12.92[((x + 0.055) / 1.055) ** 2.4])(c)'''
assert old in th
new = '''        c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]'''
th = th.replace(old, new)
wr("theme.py", th)
print("patched")
