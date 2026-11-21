import dis,marshal
f=open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc","rb"); f.read(16); code=marshal.load(f)
ins=list(dis.get_instructions(code))
for i,x in enumerate(ins):
    if x.opname in ("STORE_NAME","LOAD_NAME") and x.argval in ("BG_H","CARD_H","ACCENT_H"):
        print("---- around",i,x.opname,x.argval)
        for y in ins[max(0,i-14):i+3]:
            print(" ",y.offset,y.opname,y.argrepr)
