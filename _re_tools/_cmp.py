import dis,textwrap
tests={
"v1":"""
if key != current_name():
    self.setStyleSheet(qss(t, for_dialog=True))
    set_theme(key)
    parent = self.parent()
    if parent is not None:
        if hasattr(parent, 'apply_theme'):
            parent.apply_theme(key)
            return
        return
    return
return
""",
"v2":"""
if key != current_name():
    self.setStyleSheet(qss(t, for_dialog=True))
    set_theme(key)
    parent = self.parent()
    if parent is not None:
        if hasattr(parent, 'apply_theme'):
            parent.apply_theme(key)
            return
        return
    return
""",
"v3":"""
if key != current_name():
    self.setStyleSheet(qss(t, for_dialog=True))
    set_theme(key)
    parent = self.parent()
    if parent is not None:
        if hasattr(parent, 'apply_theme'):
            parent.apply_theme(key)
            return
    return
return
return
""",
"v4":"""
if key != current_name():
    self.setStyleSheet(qss(t, for_dialog=True))
    set_theme(key)
    parent = self.parent()
    if parent is not None:
        if hasattr(parent, 'apply_theme'):
            parent.apply_theme(key)
            return
        else:
            return
    else:
        return
else:
    return
""",
}
for name,body in tests.items():
    src="def _f(self,key,t):\n"+textwrap.indent(textwrap.dedent(body).strip()+"\n","    ")
    c=compile(src,"<t>","exec"); fn=[k for k in c.co_consts if hasattr(k,"co_code")][0]
    ins=list(dis.get_instructions(fn)); i0=[i for i,x in enumerate(ins) if x.opname=="LOAD_FAST" and x.argval=="key"][0]
    print(name, [(x.opname,x.argval if "JUMP" in x.opname else "") for x in ins[i0:] if "JUMP" in x.opname or x.opname=="RETURN_VALUE"])
