import dis, io
cands = {
 "ifFalse": "if False:\n    pass\ndef f(a=1):\n    pass\n",
 "multiline": "def f(a=1,\n      b=2):\n    '''d'''\n    pass\n",
 "trypass": "try:\n    pass\nexcept Exception:\n    pass\ndef f(a=1):\n    pass\n",
 "whilefalse": "while False:\n    pass\ndef f(a=1):\n    pass\n",
 "annassign": "x: int\ndef f(a=1):\n    pass\n",
}
for k, v in cands.items():
    print("=====", k)
    for i in dis.get_instructions(compile(v, "<t>", "exec")):
        print(" ", i.offset, i.opname, repr(i.argval), i.starts_line or "")
