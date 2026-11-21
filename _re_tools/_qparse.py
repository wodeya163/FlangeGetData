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

segments = []
cur = None
buf = []
for i, x in enumerate(ins):
    if x.opname == "BUILD_LIST" and x.arg == 0:
        cur = []
        buf = []
        continue
    if cur is None:
        continue
    if x.opname == "LIST_APPEND":
        cur.append(buf)
        buf = []
        continue
    if x.opname == "CALL_METHOD":
        segments.append(cur)
        cur = None
        continue
    buf.append(x)
print("segments", [len(s) for s in segments])

def src(seq):
    ops = [(x.opname, x.argval) for x in seq]
    if len(ops) == 1 and ops[0][0] == "LOAD_CONST" and isinstance(ops[0][1], str):
        return repr(ops[0][1])
    if len(ops) == 5 and ops[0][0] == "LOAD_FAST" and ops[1][0] == "LOAD_CONST" \
       and ops[2][0] == "BINARY_SUBSCR" and ops[3][0] == "FORMAT_VALUE":
        return 'f"""{%s[%r]}"""' % (ops[0][1], ops[1][1])
    if len(ops) == 2 and ops[0][0] == "LOAD_FAST" and ops[1][0] == "FORMAT_VALUE":
        return 'f"""{%s}"""' % ops[0][1]
    raise SystemExit("unhandled %r" % (ops,))

for si, seg in enumerate(segments):
    print("=== segment", si, len(seg))
    for s in seg[:3]:
        print("   ", src(s))
    print("   ...")
    print("   ", src(seg[-1]))
