import dis,itertools
APP="self.f(row, 1, 2)"
C1="hasattr(self, '_c')"
C2="row < len(self._c)"
def render(block,ind=0):
    out=[]
    for st in block:
        if st=="ret": out.append("    "*ind+"return")
        elif st=="app": out.append("    "*ind+APP)
        elif st=="pass": out.append("    "*ind+"pass")
        else: # ("if",cond,body)
            out.append("    "*ind+"if %s:"%st[1])
            out.extend(render(st[2],ind+1))
            if len(st)>3 and st[3]:
                out.append("    "*ind+"else:")
                out.extend(render(st[3],ind+1))
    return out
def sig(block):
    src="def g(self,row):\n"+"\n".join(render(block))+"\n"
    try: c=compile(src,"x","exec")
    except SyntaxError: return None
    f=[x for x in c.co_consts if hasattr(x,"co_code")][0]
    ins=list(dis.get_instructions(f))
    rets=[i for i,x in enumerate(ins) if x.opname=="RETURN_VALUE"]
    jumps=[]
    for i,x in enumerate(ins):
        if x.opname=="POP_JUMP_IF_FALSE":
            tgt=[j for j,y in enumerate(ins) if y.offset==x.argval]
            jumps.append(tgt[0] if tgt else None)
    return ins,jumps,rets

# enumerate: I1 body is a list containing I2 (body incl app) at some position, plus returns
bodies=[]
def lists(depth, allow_if=True):
    res=[[]]
    atoms=["ret","app","pass"]
    for a in atoms: res.append([a])
    for a in atoms:
        for b in atoms: res.append([a,b])
    for a in atoms:
        for b in atoms:
            for c in atoms: res.append([a,b,c])
    if allow_if:
        for bl in list(res):
            for pos in range(len(bl)+1):
                nb=bl[:pos]+[("if",C2,["app","ret"])]+bl[pos:]
                res.append(nb)
    return res
cnt=0
for bl in lists(1):
    body=[("if",C1,bl)]
    s=sig(body)
    if not s: continue
    ins,jumps,rets=s
    if len(jumps)==2 and len(rets)>=3:
        # map jump index to return index among returns
        def ridx(t):
            return rets.index(t) if t in rets else None
        a,b=ridx(jumps[0]),ridx(jumps[1])
        if (a,b)==(1,2):
            print("HIT"); print("\n".join(render(body))); print("jumps",jumps,"rets",rets); print("---")
            cnt+=1
print("hits",cnt)
