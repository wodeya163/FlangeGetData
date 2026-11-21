import io
p = "_decompiled_tools/密封圈选型工具V2.5/source/seal_data.py"
s = io.open(p, encoding="utf-8").read()

i = s.index("def _stretch_limit(")
j = s.index("\ndef _stretch_ok(", i)
k = s.index("\ndef compression_range(", j)

new1 = '''def _stretch_limit(d1):
    \'\'\'GB/T 3452.3-2005 附录A 表A.1 各内径允许的最大拉伸率(%)，未收录规格返回None\'\'\'
    for lo, hi, ymax in STRETCH_RATE_TABLE:
        if lo <= d1 <= hi:
            return ymax
    return None
'''
new2 = '''def _stretch_ok(stretch, ymax):
    \'\'\'拉伸率是否在表A.1推荐带内：下限0（A.1.1 最小预拉伸率可为零），上限为表A.1推荐值\'\'\'
    return 0 <= stretch <= ymax
'''
s = s[:i] + new1 + new2 + s[k:]
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
