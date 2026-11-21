import marshal, types
c = marshal.loads(open(r"密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_data.pyc","rb").read()[16:])
for k in c.co_consts:
    if isinstance(k, tuple) and len(k) == 5 and all(isinstance(x,(int,float)) for x in k):
        print(k)
