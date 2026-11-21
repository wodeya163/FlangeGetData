import re,dis
src=open(r"_re_tools\out2\seal_ui.py",encoding="utf-8-sig").read().splitlines()
def block(name):
    st=None
    for i,l in enumerate(src):
        if l.strip().startswith("def "+name+"("):
            st=i; break
    if st is None: return None
    ind=len(src[st])-len(src[st].lstrip())
    out=[src[st]]
    for l in src[st+1:]:
        if l.strip() and (len(l)-len(l.lstrip()))<=ind and re.match(r"\s*(def |class )",l): break
        out.append(l)
    return "\n".join(out)
for nm in ("paintEvent","_do_calc","_do_query","__init__"):
    b=block(nm)
    print("==",nm,"lines",len(b.splitlines()))
    try:
        c=compile("class X:\n"+b,"x","exec")
        f=[k for k in c.co_consts if hasattr(k,"co_code")][0]
        print("   insns",len(list(dis.get_instructions(f))))
    except SyntaxError as e:
        print("   SYNTAX",e)
