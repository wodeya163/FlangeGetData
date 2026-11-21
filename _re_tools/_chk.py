import dis
src=open(r"_re_tools\out2\seal_ui.py",encoding="utf-8-sig").read()
try:
    c=compile(src,"x","exec")
except SyntaxError as e:
    print("SYNTAX",e); raise SystemExit
def flat(c,p=""):
    d={p+c.co_name: len(list(dis.get_instructions(c)))}
    for k in c.co_consts:
        if isinstance(k,type(c)): d.update(flat(k,p+c.co_name+"."))
    return d
f=flat(c)
for k in f: print(f"{k:50s} {f[k]}")
