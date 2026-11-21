import dis, marshal, sys, types, importlib.util

LOAD_CONST = dis.opmap["LOAD_CONST"]
MAKE_FUNCTION = dis.opmap["MAKE_FUNCTION"]
CACHE = dis.opmap["CACHE"]

def load(p):
    return marshal.loads(open(p, "rb").read()[16:])

def patch(code):
    co = code.co_code
    words = [(co[i], co[i+1]) for i in range(0, len(co), 2)]
    none_idx = next((i for i, c in enumerate(code.co_consts) if c is None), None)
    if none_idx is None:
        return code, 0
    n = 0
    i = 0
    while i < len(words) - 1:
        op, arg = words[i]
        nop2, narg2 = words[i+1]
        if op == LOAD_CONST and nop2 == MAKE_FUNCTION and arg < 256 and none_idx < 256:
            c = code.co_consts[arg]
            if isinstance(c, types.CodeType) and c.co_name.startswith("<"):
                words[i] = (LOAD_CONST, none_idx)
                words[i+1] = (CACHE, 0)
                n += 1
        i += 1
    newconsts = []
    for c in code.co_consts:
        if isinstance(c, types.CodeType):
            nc, m = patch(c)
            n += m
            newconsts.append(nc)
        else:
            newconsts.append(c)
    out = bytes(b for w in words for b in w)
    return code.replace(co_code=out, co_consts=tuple(newconsts)), n

src, dst = sys.argv[1], sys.argv[2]
mod, n = patch(load(src))
open(dst, "wb").write(importlib.util.MAGIC_NUMBER + b"\0"*12 + marshal.dumps(mod))
print("patched", n, "->", dst)