import io,re
p=r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py"
s=io.open(p,encoding="utf-8").read()
old="""        d1 = candidate[0]
        d2 = candidate[1]
        stretch = ((d - d1) / d1) * 100
        dir_key = self._current_dir_key()
        if BACKUP_RING_PRESSURE and pressure > BACKUP_RING_PRESSURE:
            pass
        need_br = seal_type in ('static_radial', 'dynamic_recip', 'dynamic_rotate')
"""
new="""        d1, d2 = candidate[0], candidate[1]
        stretch = ((d - d1) / d1) * 100
        dir_key = self._current_dir_key()
        need_br = BACKUP_RING_PRESSURE and pressure > BACKUP_RING_PRESSURE and seal_type in ('static_radial', 'dynamic_recip', 'dynamic_rotate')
"""
assert old in s
s=s.replace(old,new)
io.open(p,"w",encoding="utf-8",newline="\n").write(s)
print("ok")
