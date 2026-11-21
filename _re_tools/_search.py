import dis, marshal, types

c = marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\theme.pyc","rb").read()[16:])
def find(c, name):
    if c.co_name == name: return c
    for k in c.co_consts:
        if isinstance(k, types.CodeType):
            r = find(k, name)
            if r: return r
orig = find(c, "_on_pick")
o = [(i.opname, i.argval if not (i.opcode in dis.hasjrel or i.opcode in dis.hasjabs) else i.argval) for i in dis.get_instructions(orig)]
otail = o[121:]   # from offset 242

PRE = """def _pick(self, idx):
    key = self.combo.itemData(idx)
    if key not in THEMES:
        return None
    t = THEMES[key]
    parent = None
    if key != current_name():
        self.setStyleSheet(qss(t, for_dialog=True))
        set_theme(key)
        parent = self.parent()
"""
POST = """
"""

variants = {
 "v1": """        if parent is not None:
            if hasattr(parent, 'apply_theme'):
                parent.apply_theme(key)
                return None
            return None
        return None
""",
 "v2": """        if parent is not None and hasattr(parent, 'apply_theme'):
            parent.apply_theme(key)
            return None
        return None
""",
 "v3": """        if parent is not None:
            if hasattr(parent, 'apply_theme'):
                parent.apply_theme(key)
                return None
        return None
""",
 "v4": """        if parent is not None:
            if hasattr(parent, 'apply_theme'):
                parent.apply_theme(key)
                return None
            return None
    return None
""",
 "v5": """        if parent is not None and hasattr(parent, 'apply_theme'):
            parent.apply_theme(key)
            return None
        return None
    return None
""",
 "v6": """        if parent is not None:
            if hasattr(parent, 'apply_theme'):
                parent.apply_theme(key)
                return None
            else:
                return None
        else:
            return None
""",
 "v7": """        if parent is None:
            return None
        if not hasattr(parent, 'apply_theme'):
            return None
        parent.apply_theme(key)
        return None
""",
 "v8": """        if parent is not None:
            if hasattr(parent, 'apply_theme'):
                parent.apply_theme(key)
                return None
            return None
        else:
            return None
""",
 "v9": """        if parent is not None and hasattr(parent, 'apply_theme'):
            parent.apply_theme(key)
            return None
        else:
            return None
""",
}

def sig(fn):
    return [(i.opname, i.argval) for i in dis.get_instructions(fn)]

for name, body in variants.items():
    src = PRE + body + POST
    try:
        mod = compile(src, "<v>", "exec")
    except SyntaxError as e:
        print(name, "SYNTAX", e); continue
    fn = next(x for x in mod.co_consts if isinstance(x, types.CodeType))
    s = sig(fn)
    tail = s[-len(otail):] if len(s) >= len(otail) else s
    ok = tail == otail
    print(name, "len", len(s), "MATCH" if ok else "no")
    if not ok:
        print("   ", tail[-8:])
print("orig tail len", len(otail))
print("orig", otail[-8:])
