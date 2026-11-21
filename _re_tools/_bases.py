import dis,marshal
co=marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb").read()[16:])
ins=list(dis.get_instructions(co))
for i,x in enumerate(ins):
    if x.opname=="STORE_NAME" and x.argval in ("OringTab","GrooveTab","MaterialTab","KnowledgeTab","MainWindow","GrooveWidget"):
        print("==",x.argval)
        for y in ins[i-7:i+1]: print("  ",y.offset,y.opname,y.argrepr)
