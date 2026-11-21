import dis
variants = {
"E": """def f(self,row,col):
    if hasattr(self,'_candidates'):
        if row < len(self._candidates):
            self._show_groove_for(self._candidates[row], self._seal_type, self._pressure)
            return None
    else:
        return None
    return None
""",
"F": """def f(self,row,col):
    if hasattr(self,'_candidates'):
        if row < len(self._candidates):
            self._show_groove_for(self._candidates[row], self._seal_type, self._pressure)
            return None
        else:
            pass
    else:
        return None
    return None
""",
}
for k,src in variants.items():
    ns={}; exec(src,ns)
    print('='*10,k)
    for i in dis.get_instructions(ns['f']): print(i.offset,i.opname,i.argrepr)
