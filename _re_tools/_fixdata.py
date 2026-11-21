import re, io
p = r"_decompiled_tools\密封圈选型工具V2.5\source\seal_data.py"
s = io.open(p, encoding="utf-8").read()

s = s.replace("    5.3: 0.13,\n    7: 0.15 }", "    5.3: 0.13,\n    7.0: 0.15 }")

s = s.replace("""    elif seal_type in ('dynamic_rotate', 'low_friction'):
        w = COMPRESSION_HYD_DYN.get(d2)
        if w:
            return (w[0], w[1], '参考液压动密封(表A.3，标准未单列本工况)；行业资料旋转工况常用约2%~5%，以厂家样本为准')
        return None
    table = COMPRESSION_RADIAL
    return table.get(d2)""", """    elif seal_type in ('dynamic_rotate', 'low_friction'):
        w = COMPRESSION_HYD_DYN.get(d2)
        if w:
            return (w[0], w[1], '参考液压动密封(表A.3，标准未单列本工况)；行业资料旋转工况常用约2%~5%，以厂家样本为准')
        return None
    else:
        table = COMPRESSION_RADIAL
    return table.get(d2)""")

s = s.replace("""                if -stretch > kmax:
                    continue
            else:
                if d1 > d_shaft:
                    continue
                kmax = _stretch_limit(d1)
            if kmax is None:
                continue
            if not _stretch_ok(stretch, kmax):
                continue
            base_pri""", """                if -stretch > kmax:
                    continue
            else:
                if d1 > d_shaft:
                    continue
                kmax = _stretch_limit(d1)
                if kmax is None:
                    continue
                if not _stretch_ok(stretch, kmax):
                    continue
            base_pri""")

s = s.replace("""    return {
        3.55: 2,
        2.65: 2,""", """    return {
        3.55: 3,
        2.65: 2,""")

s = s.replace("""        (h, b) = GROOVE_AXIAL[d2]
        r1 = GROOVE_BOTTOM_R.get(d2)
    elif d2 not in GROOVE_RADIAL:
        return None
    row = GROOVE_RADIAL[d2]
    if seal_type == 'hydraulic_dynamic':
        h = row[1]
    elif seal_type == 'pneumatic_dynamic':
        h = row[2]
    elif seal_type in ('dynamic_recip', 'dynamic_rotate'):
        h = row[1]
    else:
        h = row[0]
    if double_backup:
        b = row[6]
    elif with_backup:
        b = row[5]
    elif seal_type == 'pneumatic_dynamic':
        b = row[3]
    else:
        b = row[4]
    r1 = GROOVE_BOTTOM_R.get(d2)
""", """        (h, b) = GROOVE_AXIAL[d2]
        r1 = GROOVE_BOTTOM_R.get(d2)
    else:
        if d2 not in GROOVE_RADIAL:
            return None
        row = GROOVE_RADIAL[d2]
        if seal_type == 'hydraulic_dynamic':
            h = row[1]
        elif seal_type == 'pneumatic_dynamic':
            h = row[2]
        elif seal_type in ('dynamic_recip', 'dynamic_rotate'):
            h = row[1]
        else:
            h = row[0]
        if double_backup:
            b = row[6]
        elif with_backup:
            b = row[5]
        elif seal_type == 'pneumatic_dynamic':
            b = row[3]
        else:
            b = row[4]
        r1 = GROOVE_BOTTOM_R.get(d2)
""")

s = s.replace("""    else:
        dir_info = None
    if not with_backup:
        pass
    return {""", """    else:
        dir_info = None
    return {""")

s = s.replace("""        'd2': d2,
        'with_backup': double_backup,""", """        'd2': d2,
        'with_backup': with_backup or double_backup,""")

s = s.replace('''mkey = _MEDIA_RATE_KEY.get(medium or "").strip()''', '''mkey = _MEDIA_RATE_KEY.get((medium or "").strip())''')

s = s.replace("""    if not need and review:
        review.append('如挤出间隙偏大""", """    if not need and not review:
        review.append('如挤出间隙偏大""")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("done")
