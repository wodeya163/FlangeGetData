import dis,marshal,sys,types
def load(p): return marshal.loads(open(p,"rb").read()[16:])
def find(c,n):
    for k in c.co_consts:
        if isinstance(k,types.CodeType):
            if k.co_name==n: return k
            r=find(k,n)
            if r: return r
def sig(c):
    out=[]
    for i in dis.get_instructions(c):
        if i.opcode in dis.hasjrel or i.opcode in dis.hasjabs: out.append((i.opname,"J",i.argval))
        elif isinstance(i.argval, types.CodeType): out.append((i.opname,"<code %s>"%i.argval.co_name,i.argval.co_name))
        else: out.append((i.opname,repr(i.argval),i.argval))
    return out
pyc,src,n=sys.argv[1],sys.argv[2],sys.argv[3]
co=find(load(pyc),n); new=find(compile(open(src,encoding="utf-8-sig").read(),"x","exec"),n)
a,b=sig(co),sig(new); print(n,"orig",len(a),"new",len(b))
i=0
while i<min(len(a),len(b)) and a[i][:2]==b[i][:2]: i+=1
print("first diff at",i)
for j in range(max(0,i-8),min(len(a),i+14)):
    print("O",j,a[j])
for j in range(max(0,i-8),min(len(b),i+14)):
    print("N",j,b[j])
