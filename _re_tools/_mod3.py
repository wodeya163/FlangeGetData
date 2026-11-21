import dis,marshal
f=open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb"); f.read(16); code=marshal.load(f)
ins=list(dis.get_instructions(code))
for x in ins[165:205]: print(x.offset,x.opname,x.argrepr)
print("TOTAL",len(ins))
