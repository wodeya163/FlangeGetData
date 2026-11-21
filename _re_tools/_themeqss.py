import ast, io, sys

p = r"_decompiled_tools\密封圈选型工具V2.5\source\theme.py"
lines = io.open(p, encoding="utf-8").read().splitlines()

def fragments(expr):
    # expr is Subscript chain rooted at List
    slices = []
    node = expr
    while isinstance(node, ast.Subscript):
        slices.append(node.slice)
        node = node.value
    if not isinstance(node, ast.List):
        raise SystemExit("base is %r" % type(node))
    slices.reverse()
    return slices

def render(sl):
    if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
        return repr(sl.value)
    if isinstance(sl, ast.JoinedStr):
        parts = []
        for v in sl.values:
            if isinstance(v, ast.Constant):
                parts.append(v.value)
            elif isinstance(v, ast.FormattedValue):
                assert v.format_spec is None and v.conversion == -1
                parts.append("{" + ast.unparse(v.value) + "}")
        return 'f"""' + "".join(parts) + '"""'
    return ast.unparse(sl)

line231 = lines[230]
assign = ast.parse(line231).body[0]
assert isinstance(assign, ast.Assign) and assign.targets[0].id == "common", ast.dump(assign)[:200]
frag_a = fragments(assign.value)

line234 = lines[233]
ret = ast.parse(line234).body[0]
assert isinstance(ret, ast.Return), ast.dump(ret)[:200]
expr = ret.value
assert isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add), ast.dump(expr)[:200]
left, right = expr.left, expr.right
assert isinstance(left, ast.Name) and left.id == "common"
assert isinstance(right, ast.Call) and isinstance(right.func, ast.Attribute) and right.func.attr == "join"
frag_b = fragments(right.args[0])

def block(frags, indent="        "):
    out = ["''.join(["]
    for f in frags:
        out.append(indent + render(f) + ",")
    out.append("    ])")
    return "\n".join(out)

new231 = "    common = " + block(frag_a)
new234 = "    return common + " + block(frag_b)

out = io.open(p, encoding="utf-8").read().split("\n")
out[230] = new231
out[233] = new234
io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("frags", len(frag_a), len(frag_b))
