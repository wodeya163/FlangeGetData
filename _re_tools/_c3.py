import marshal, io
c = marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_data.pyc","rb").read()[16:])
vals = [k for k in c.co_consts if isinstance(k, tuple) and len(k)==3 and isinstance(k[2], str)]
print(len(vals))
for v in vals:
    print(repr(v))
