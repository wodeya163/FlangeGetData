import dis, itertools, sys
TARGET = [
("LOAD_FAST","key"),("LOAD_GLOBAL","current_name"),("CALL_FUNCTION","0"),("COMPARE_OP","!="),
("POP_JUMP_IF_FALSE","J"),("LOAD_FAST","self"),("LOAD_METHOD","setStyleSheet"),("LOAD_GLOBAL","qss"),
("LOAD_FAST","t"),("LOAD_CONST",True),("LOAD_CONST",("for_dialog",)),("CALL_FUNCTION_KW","2"),
("CALL_METHOD","1"),("POP_TOP",None),("LOAD_GLOBAL","set_theme"),("LOAD_FAST","key"),
("CALL_FUNCTION","1"),("POP_TOP",None),("LOAD_FAST","self"),("LOAD_METHOD","parent"),
("CALL_METHOD","0"),("STORE_FAST","parent"),("LOAD_FAST","parent"),("LOAD_CONST",None),
("IS_OP","1"),("POP_JUMP_IF_FALSE","J"),("LOAD_GLOBAL","hasattr"),("LOAD_FAST","parent"),
("LOAD_CONST","apply_theme"),("CALL_FUNCTION","2"),("POP_JUMP_IF_FALSE","J"),("LOAD_FAST","parent"),
("LOAD_METHOD","apply_theme"),("LOAD_FAST","key"),("CALL_METHOD","1"),("POP_TOP",None),
("LOAD_CONST",None),("RETURN_VALUE",None),("LOAD_CONST",None),("RETURN_VALUE",None),
("LOAD_CONST",None),("RETURN_VALUE",None),("LOAD_CONST",None),("RETURN_VALUE",None),
]
TARGET_T = [141,143,145]
TARGET_LEN=len(TARGET)

def sig(body):
    src="def _f(self, key, t, current_name, THEMES, qss, set_theme):\n" + "\n".join("    "+l for l in body.split("\n"))
    try:
        c=compile(src,"<t>","exec")
    except SyntaxError:
        return None
    fn=[k for k in c.co_consts if hasattr(k,"co_code")][0]
    ins=list(dis.get_instructions(fn))
    idx=[i for i,x in enumerate(ins) if x.opname=="LOAD_FAST" and x.argval=="key"]
    if not idx: return None
    i0=idx[0]
    tail=ins[i0:i0+TARGET_LEN]
    if len(tail)<TARGET_LEN: return None
    out=[]; base=i0
    for k,x in enumerate(tail):
        if x.opname in ("POP_JUMP_IF_FALSE","POP_JUMP_IF_TRUE","JUMP_ABSOLUTE","JUMP_FORWARD","POP_JUMP_FORWARD_IF_FALSE","POP_JUMP_BACKWARD_IF_FALSE"):
            # map target offset to index
            tgt=None
            for j,y in enumerate(ins):
                if y.offset==x.argval: tgt=j-i0; break
            out.append((x.opname,tgt))
        else:
            v=x.argval
            if x.opname=="LOAD_CONST": v=x.argval
            out.append((x.opname,v))
    return out

A="self.setStyleSheet(qss(t, for_dialog=True))\nset_theme(key)\nparent = self.parent()"
# grammar
CONDS={"c1":"key != current_name()","c2":"parent is not None","c3":"hasattr(parent, 'apply_theme')"}
def blocks(depth):
    # yield list of statements (as source lines list) including empty
    simple=["return","pass",A,"parent = self.parent()","set_theme(key)"]
    res=[[]]
    for s in simple:
        res.append([s])
    if depth>0:
        for cname,c in CONDS.items():
            for body in blocks(depth-1):
                for els in blocks(depth-1):
                    if not body and not els: continue
                    st="if %s:\n"%c + "\n".join("    "+x for x in body) if body else "if %s:\n    pass"%c
                    if els:
                        st+="\nelse:\n"+"\n".join("    "+x for x in els)
                    res.append([st])
        # sequences
        base=res[:]
        for a in base[:12]:
            for b in base[:12]:
                if a and b: res.append(a+b)
    return res
seen=set(); hits=[]
for body in blocks(2):
    src="\n".join(body)
    if src in seen: continue
    seen.add(src)
    s=sig(src)
    if s is None: continue
    if len(s)!=TARGET_LEN: continue
    ok=True
    for (a,b),(c,d) in zip(s,TARGET):
        if a!=c: ok=False;break
        if c in ("POP_JUMP_IF_FALSE",):
            pass
        else:
            if b!=d: ok=False;break
    if ok:
        js=[v for (o,v) in s if o=="POP_JUMP_IF_FALSE"]
        if js==TARGET_T:
            hits.append(src); print("HIT:\n"+src+"\n----")
print("total tested",len(seen),"hits",len(hits))
