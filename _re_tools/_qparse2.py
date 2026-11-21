import dis, marshal, io, types

pyc = r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\theme.pyc"
root = marshal.loads(open(pyc, "rb").read()[16:])

def find(c, name):
    if c.co_name == name:
        return c
    for k in c.co_consts:
        if isinstance(k, types.CodeType):
            r = find(k, name)
            if r:
                return r

code = find(root, "qss")
ins = list(dis.get_instructions(code))

segments, cur, buf = [], None, []
for x in ins:
    if x.opname == "BUILD_LIST" and x.arg == 0:
        cur, buf = [], []
        continue
    if cur is None:
        continue
    if x.opname == "LIST_APPEND":
        cur.append(buf); buf = []
        continue
    if x.opname == "CALL_METHOD":
        segments.append(cur); cur = None
        continue
    buf.append(x)

def src(seq):
    ops = [(x.opname, x.argval) for x in seq]
    if len(ops) == 1 and ops[0][0] == "LOAD_CONST" and isinstance(ops[0][1], str):
        return repr(ops[0][1])
    if len(ops) == 4 and ops[0][0] == "LOAD_FAST" and ops[1][0] == "LOAD_CONST" \
       and ops[2][0] == "BINARY_SUBSCR" and ops[3][0] == "FORMAT_VALUE":
        return 'f"""{%s[%r]}"""' % (ops[0][1], ops[1][1])
    if len(ops) == 2 and ops[0][0] == "LOAD_FAST" and ops[1][0] == "FORMAT_VALUE":
        return 'f"""{%s}"""' % ops[0][1]
    raise SystemExit("unhandled %r" % (ops,))

def block(seg):
    out = ["''.join(["]
    for s in seg:
        out.append("        " + src(s) + ",")
    out.append("    ])")
    return "\n".join(out)

p = r"_decompiled_tools\密封圈选型工具V2.5\source\theme.py"
text = io.open(p, encoding="utf-8").read()
lines = text.split("\n")
start = next(i for i, l in enumerate(lines) if l.startswith("def qss("))
end = next(i for i, l in enumerate(lines) if l.startswith("def contrast("))

head = """def qss(t=None, for_dialog=False):
    '''生成全局样式表（挂在 MainWindow / 各对话框上，随换肤整体重挂）。

    for_dialog=True 时输出精简的一条（对话框背景与文字），避免对话框里
    出现主窗口的 GroupBox/页签规则影响布局。
    '''
    t = t or current()
    r = t['radius']
    arrow = t['text2']
    (arrow_up, arrow_dn) = _arrow_pngs(arrow)
    common = """ + block(segments[0]) + """
    if for_dialog:
        return common
    return common + """ + block(segments[1]).lstrip() + "\n"

lines[start:end] = head.split("\n")
io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("ok", len(segments[0]), len(segments[1]))
