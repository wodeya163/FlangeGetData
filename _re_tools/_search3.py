import dis, marshal, types
c = marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\theme.pyc","rb").read()[16:])
def find(c, name):
    if c.co_name == name: return c
    for k in c.co_consts:
        if isinstance(k, types.CodeType):
            r = find(k, name)
            if r: return r
orig = find(c, "_on_pick")
def rel(fn, n=26):
    ins = list(dis.get_instructions(fn))[-n:]
    base = ins[0].offset
    return [(i.opname, ("->%d" % ((i.argval-base)//2)) if (i.opcode in dis.hasjrel or i.opcode in dis.hasjabs) else i.argval) for i in ins]
target = rel(orig)

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
I = "        "
def test(name, body):
    try:
        mod = compile(PRE + body, "<v>", "exec")
    except SyntaxError as e:
        print(name, "SYNTAX"); return
    fn = next(x for x in mod.co_consts if isinstance(x, types.CodeType))
    r = rel(fn)
    hit = r == target
    print(name, "MATCH" if hit else "no", [x for x in r if x[0].startswith("POP_JUMP")])
    if hit:
        print(PRE+body)

test("a1", I+"if parent is not None:\n"+I+"    if hasattr(parent, 'apply_theme'):\n"+I+"        parent.apply_theme(key)\n"+I+"        return None\n"+I+"return None\n"+I+"return None\n")
test("a2", I+"if parent is not None:\n"+I+"    if hasattr(parent, 'apply_theme'):\n"+I+"        parent.apply_theme(key)\n"+I+"        return None\n"+I+"    return None\n"+I+"return None\n"+I+"return None\n")
test("a3", I+"if parent is not None:\n"+I+"    if hasattr(parent, 'apply_theme'):\n"+I+"        parent.apply_theme(key)\n"+I+"        return None\n"+I+"    return None\n"+I+"else:\n"+I+"    return None\n"+I+"return None\n")
test("a4", I+"if parent is not None:\n"+I+"    if hasattr(parent, 'apply_theme'):\n"+I+"        parent.apply_theme(key)\n"+I+"        return None\n"+I+"    else:\n"+I+"        return None\n"+I+"else:\n"+I+"    return None\n"+I+"return None\n")
test("a5", I+"if parent is not None:\n"+I+"    if hasattr(parent, 'apply_theme'):\n"+I+"        parent.apply_theme(key)\n"+I+"    return None\n"+I+"else:\n"+I+"    return None\n"+I+"return None\n")
test("a6", I+"if parent is not None and hasattr(parent, 'apply_theme'):\n"+I+"    parent.apply_theme(key)\n"+I+"    return None\n"+I+"return None\n"+I+"return None\n")
test("a7", I+"if parent is not None:\n"+I+"    if hasattr(parent, 'apply_theme'):\n"+I+"        parent.apply_theme(key)\n"+I+"        return None\n"+I+"return None\n")
test("a8", I+"if parent is not None:\n"+I+"    if hasattr(parent, 'apply_theme'):\n"+I+"        parent.apply_theme(key)\n"+I+"        return None\n"+I+"    return None\n"+I+"return None\n")
test("a9", I+"if parent is not None:\n"+I+"    if hasattr(parent, 'apply_theme'):\n"+I+"        parent.apply_theme(key)\n"+I+"        return None\n"+I+"    else:\n"+I+"        return None\n"+I+"return None\n")
test("a10", I+"if parent is None:\n"+I+"    return None\n"+I+"if hasattr(parent, 'apply_theme'):\n"+I+"    parent.apply_theme(key)\n"+I+"    return None\n"+I+"return None\n")
