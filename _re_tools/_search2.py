import dis, marshal, types, itertools

c = marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\theme.pyc","rb").read()[16:])
def find(c, name):
    if c.co_name == name: return c
    for k in c.co_consts:
        if isinstance(k, types.CodeType):
            r = find(k, name)
            if r: return r
orig = find(c, "_on_pick")

def rel(fn, n=26):
    ins = list(dis.get_instructions(fn))
    win = ins[-n:]
    base = win[0].offset
    out = []
    for i in win:
        if i.opcode in dis.hasjrel or i.opcode in dis.hasjabs:
            out.append((i.opname, "->%d" % ((i.argval - base) // 2)))
        else:
            out.append((i.opname, i.argval))
    return out

target = rel(orig)
print("ORIG", target)

PRE = """def _pick(self, idx):
    key = self.combo.itemData(idx)
    if key not in THEMES:
        return None
    t = THEMES[key]
    if key != current_name():
        self.setStyleSheet(qss(t, for_dialog=True))
        set_theme(key)
        parent = self.parent()
"""

bodies = {}
A = "        "
def add(name, body):
    bodies[name] = body

add("n1", A+"if parent is not None:\n"+A+"    if hasattr(parent, 'apply_theme'):\n"+A+"        parent.apply_theme(key)\n"+A+"        return None\n"+A+"    return None\n"+A+"return None\n")
add("n2", A+"if parent is not None:\n"+A+"    if hasattr(parent, 'apply_theme'):\n"+A+"        parent.apply_theme(key)\n"+A+"        return None\n"+A+"    return None\n")
add("n3", A+"if parent is not None:\n"+A+"    if hasattr(parent, 'apply_theme'):\n"+A+"        parent.apply_theme(key)\n"+A+"    return None\n"+A+"return None\n")
add("n4", A+"if parent is not None:\n"+A+"    if hasattr(parent, 'apply_theme'):\n"+A+"        parent.apply_theme(key)\n"+A+"        return None\n"+A+"else:\n"+A+"    return None\n"+A+"return None\n")
add("n5", A+"if parent is not None:\n"+A+"    if hasattr(parent, 'apply_theme'):\n"+A+"        parent.apply_theme(key)\n"+A+"        return None\n"+A+"    return None\n"+A+"else:\n"+A+"    return None\n")
add("n6", A+"if parent is not None and hasattr(parent, 'apply_theme'):\n"+A+"    parent.apply_theme(key)\n"+A+"    return None\n"+A+"else:\n"+A+"    return None\n"+A+"return None\n")
add("n7", A+"if parent is None:\n"+A+"    return None\n"+A+"if not hasattr(parent, 'apply_theme'):\n"+A+"    return None\n"+A+"parent.apply_theme(key)\n"+A+"return None\n")
add("n8", A+"if parent is not None:\n"+A+"    if hasattr(parent, 'apply_theme'):\n"+A+"        parent.apply_theme(key)\n"+A+"        return None\n"+A+"    else:\n"+A+"        return None\n"+A+"return None\n")
add("n9", A+"if parent is not None and hasattr(parent, 'apply_theme'):\n"+A+"    parent.apply_theme(key)\n"+A+"    return None\n"+A+"return None\n")
add("n10", A+"if parent is not None:\n"+A+"    if hasattr(parent, 'apply_theme'):\n"+A+"        parent.apply_theme(key)\n"+A+"        return None\n"+A+"return None\n"+A+"return None\n")
add("n11", A+"if parent is not None:\n"+A+"    if hasattr(parent, 'apply_theme'):\n"+A+"        parent.apply_theme(key)\n"+A+"    else:\n"+A+"        return None\n"+A+"else:\n"+A+"    return None\n"+A+"return None\n")

for name, body in bodies.items():
    src = PRE + body
    try:
        mod = compile(src, "<v>", "exec")
    except SyntaxError as e:
        print(name, "SYNTAX", e); continue
    fn = next(x for x in mod.co_consts if isinstance(x, types.CodeType))
    r = rel(fn)
    print(name, "MATCH" if r == target else "no", len(list(dis.get_instructions(fn))))
