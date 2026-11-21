import io
p=r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py"
s=io.open(p,encoding="utf-8").read()
old="""            else:
                w_min = None
                w_max = None
                gi.append('压缩率推荐带：本工况标准未收录，暂无数据（—）')
"""
new="""            else:
                w_min = w_max = None
                gi.append('压缩率推荐带：本工况标准未收录，暂无数据（—）')
"""
assert old in s
s=s.replace(old,new)
io.open(p,"w",encoding="utf-8",newline="\n").write(s)
print("ok")
