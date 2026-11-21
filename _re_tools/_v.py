import dis
variants={
"a":"if hasattr(self, '_c'):\n    if row < len(self._c):\n        self.f(row, 1, 2)\n        return\n    return\nreturn\n",
"b":"if hasattr(self, '_c'):\n    if row < len(self._c):\n        self.f(row, 1, 2)\n        return\nreturn\nreturn\n",
"c":"if not hasattr(self, '_c'):\n    return\nif row >= len(self._c):\n    return\nself.f(row,1,2)\nreturn\n",
}
for k,v in variants.items():
    src="def g(self,row):\n"+"".join("    "+l for l in v.splitlines(True))
    c=compile(src,"x","exec"); f=[x for x in c.co_consts if hasattr(x,"co_code")][0]
    print("==",k)
    for i in dis.get_instructions(f): print(" ",i.offset,i.opname,i.argrepr)
