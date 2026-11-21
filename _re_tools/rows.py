import os, sys, dis, marshal, types, json

def load_pyc(p): return marshal.loads(open(p, "rb").read()[16:])
def walk(code, prefix=""):
    n = prefix + ("" if code.co_name == "<module>" else code.co_name)
    yield n.lstrip("."), code
    for c in code.co_consts:
        if isinstance(c, types.CodeType): yield from walk(c, n + ".")
def _res(off, surv, fwd):
    seen=set()
    while off not in surv:
        if off in seen: return None
        seen.add(off); off=fwd.get(off)
        if off is None: return None
    return surv[off]
def sig(code):
    ins=list(dis.get_instructions(code))
    def show(a):
        if isinstance(a, types.CodeType): return "<code %s>"%a.co_name
        if isinstance(a,(set,frozenset)): return "{%s}"%", ".join(sorted(show(x) for x in a))
        if isinstance(a,(list,tuple)):
            i=", ".join(show(x) for x in a)
            return "[%s]"%i if isinstance(a,list) else ("(%s,)"%i if len(a)==1 else "(%s)"%i)
        if not isinstance(a,bool) and isinstance(a,(int,float)): return "num(%r)"%float(a)
        return repr(a)
    fwd={}
    for k,i in enumerate(ins):
        if i.opcode in dis.hasjrel or i.opcode in dis.hasjabs: fwd[i.offset]=i.argval
        elif k+1<len(ins): fwd[i.offset]=ins[k+1].offset
    kept=[i for i in ins if i.opname not in ("NOP","JUMP_FORWARD","EXTENDED_ARG")]
    surv={i.offset:k for k,i in enumerate(kept)}
    out=[]
    for k,i in enumerate(kept):
        a,op=i.argval,i.opname
        if op in ("LOAD_METHOD","LOAD_ATTR") and k+1<len(kept) and kept[k+1].opname=="PRECALL": op="LOAD_CALLABLE"
        out.append((op, "->%s"%(_res(a,surv,fwd) if _res(a,surv,fwd) is not None else "?") if (i.opcode in dis.hasjrel or i.opcode in dis.hasjabs) else show(a)))
    return out

app, ver = sys.argv[1], sys.argv[2]
base=os.path.join("_decompiled_tools",app); src_root=os.path.join(base,"source"); pyc_root=os.path.join(base,"original_pyc")
rows=[]
for dp,_,fs in os.walk(src_root):
    if "__pycache__" in dp: continue
    for f in sorted(fs):
        if not f.endswith(".py"): continue
        s=os.path.join(dp,f); rel=os.path.relpath(s,src_root)
        pc=os.path.join(pyc_root, rel[:-3]+".pyc")
        if not os.path.exists(pc):
            rows.append({"module":rel.replace("\\","/"),"status":"nopyc"}); continue
        try:
            o=dict(walk(load_pyc(pc)))
            try: n=dict(walk(compile(open(s,encoding="utf-8").read(),s,"exec",dont_inherit=True)))
            except SyntaxError as e:
                rows.append({"module":rel.replace("\\","/"),"status":"syntax","objects":len(o),"line":e.lineno}); continue
        except Exception as e:
            rows.append({"module":rel.replace("\\","/"),"status":"error","detail":str(e)[:80]}); continue
        miss=[x for x in o if x not in n]; extra=[x for x in n if x not in o]
        diff=[x for x in o if x in n and sig(o[x])!=sig(n[x])]
        st="exact" if not miss and not extra and not diff else "diff"
        rows.append({"module":rel.replace("\\","/"),"status":st,"objects":len(o),"exact":len(o)-len(diff)-len(miss),"diff":len(diff),"missing":len(miss),"extra":len(extra)})
print(json.dumps({"app":app,"python":ver,"rows":rows},ensure_ascii=False))
