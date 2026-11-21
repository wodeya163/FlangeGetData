import dis, marshal
c = marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_data.pyc","rb").read()[16:])
for i in dis.get_instructions(c):
    if 600 <= i.offset <= 700:
        print(i.offset, i.opname, repr(i.argval), "LINE" if i.starts_line else "", i.starts_line or "")
