import io
p = "_decompiled_tools/密封圈选型工具V2.5/source/seal_data.py"
s = io.open(p, encoding="utf-8").read()


def rep(old, new, count=1):
    global s
    assert old in s, old[:60]
    s = s.replace(old, new, count)


rep("    7: (109, 670) }", "    7.0: (109, 670) }")

i = s.index("def groove_depth_limits(")
j = s.index("\nSTRETCH_RATE_TABLE = ", i)
s = s[:i] + '''def groove_depth_limits(d2, seal_type):
    \'\'\'按工况取沟槽深度极限值（GB/T 3452.3-2005 表A.3/表A.4，资料性）
    返回 (t_min, t_max) 或 None\'\'\'
    if seal_type == "static_axial":
        return DEPTH_AXIAL.get(d2)
    elif seal_type in ("hydraulic_dynamic", "dynamic_recip", "dynamic_rotate", "low_friction"):
        return DEPTH_HYD_DYN.get(d2)
    elif seal_type == "pneumatic_dynamic":
        return DEPTH_PNEU_DYN.get(d2)
    return DEPTH_RADIAL_STATIC.get(d2)
''' + s[j:]

i = s.index("def _precompression_limit(")
j = s.index("\nMATERIALS = ", i)
s = s[:i] + '''def _precompression_limit(d1, seal_type):
    \'\'\'表A.2 各内径允许的最大预压缩率(%)（活塞杆密封，|拉伸率|为负）；
    未收录返回 None；末档仅静密封，动密封取不到时返回 None\'\'\'
    for lo, hi, kmax, scope in PRECOMPRESSION_TABLE:
        if lo <= d1 <= hi:
            if scope == "仅静密封" and seal_type not in ("static_radial", "static_axial"):
                return None
            return kmax
    return None
''' + s[j:]

# recommend_oring branch structure
rep('''            if rod_mode:
                if d1 < d_shaft:
                    continue
                kmax = _precompression_limit(d1, seal_type)
                if kmax is None:
                    continue
                if -stretch > kmax:
                    continue
                elif d1 > d_shaft:
                    continue
            kmax = _stretch_limit(d1)''',
    '''            if rod_mode:
                if d1 < d_shaft:
                    continue
                kmax = _precompression_limit(d1, seal_type)
                if kmax is None:
                    continue
                if -stretch > kmax:
                    continue
            else:
                if d1 > d_shaft:
                    continue
                kmax = _stretch_limit(d1)''')
rep("            stretch_bonus = -abs(stretch) / 100\n",
    "            stretch_bonus = -abs(stretch) / 100.0\n")

# _oring_priority
rep('''    if seal_type in ('dynamic_recip', 'dynamic_rotate'):
        return {
            1.8: 3,
            2.65: 3,
            3.55: 2,
            5.3: 1,
            7: 0 }.get(d2, 0)
    return {
        3.55: None,
        2.65: 2,
        5.3: 2,
        1.8: 1,
        7: 1 }.get(d2, 0)''',
    '''    if seal_type in ("dynamic_recip", "dynamic_rotate"):
        return {
            1.8: 3,
            2.65: 3,
            3.55: 2,
            5.3: 1,
            7.0: 0}.get(d2, 0)
    return {
        3.55: 2,
        2.65: 2,
        5.3: 2,
        1.8: 1,
        7.0: 1}.get(d2, 0)''')

# axial_diameter_limits conditions
rep("    if not d1 is None and d2 is None or pressure_dir:",
    "    if d1 is None or d2 is None or not pressure_dir:")
rep("    if None == 'internal':", "    if pressure_dir == 'internal':")
rep("    if None == 'external':", "    if pressure_dir == 'external':")
rep("""    return {
        'undefined': None,
        'note': '轴向密封需先选择受内压/受外压' }""",
    """    return {
        'undefined': True,
        'note': '轴向密封需先选择受内压/受外压' }""")

# calc_groove
rep("        (h, b) = None[d2]", "        (h, b) = GROOVE_AXIAL[d2]")

# get_compression_check
i = s.index("def get_compression_check(")
j = s.index("\ndef recommend_material(", i)
s = s[:i] + '''def get_compression_check(d2, h, seal_type):
    \'\'\'
    验算压缩率（推荐范围按表A.3/表A.4 分工况取值）
    返回: (压缩率%, 是否在推荐带内或None, 提示)；无标准数据时判定为 None
    \'\'\'
    w = (d2 - h) / d2 * 100
    rng = compression_range(d2, seal_type)
    if not rng:
        return (w, None, f"压缩率 = {w:.1f}%（本工况无标准推荐带）")
    (w_min, w_max, _label) = rng
    return (w, w_min <= w <= w_max, f"压缩率 = {w:.1f}%")
''' + s[j:]

# recommend_material_ex: docstring + get()
i = s.index("def recommend_material_ex(")
j = s.index("\ndef recommend_backup_ring(", i)
s = s[:i] + '''def recommend_material_ex(medium, temp_min, temp_max):
    \'\'\'同 recommend_material，并附带被筛掉的材料及原因（界面透明展示用）。
    起因（2026-10-24 试用单 T1）：默认温度-20℃把丁腈（长期低温-10℃，手册表3-3-2
    原文值）静默滤掉，读者看不到最常用材料的存在；改为明示「未列入+原因」。
    返回 (ok_list, excluded_list)；ok 项为 (代号, 说明)，
    excluded 项为 (代号, 原因)。\'\'\'
    mkey = _MEDIA_RATE_KEY.get(medium or "").strip()
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
''' + s[j:]

rep("    return None > BACKUP_RING_PRESSURE", "    return pressure_mpa > BACKUP_RING_PRESSURE")
rep("    p = pressure_mpa if pressure_mpa is not None else 0\n",
    "    p = pressure_mpa if pressure_mpa is not None else 0.0\n")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
