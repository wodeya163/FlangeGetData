import io,sys
p=r"_decompiled_tools\密封圈选型工具V2.5\source\theme.py"
s=open(p,encoding="utf-8-sig").read()
old = """        if key != current_name():
            self.setStyleSheet(qss(t, for_dialog=True))
            set_theme(key)
            parent = self.parent()
            if parent is not None:
                if hasattr(parent, 'apply_theme'):
                    parent.apply_theme(key)
                    return None
                return None
            return None
        return None
"""
new = """        if key != current_name():
            self.setStyleSheet(qss(t, for_dialog=True))
            set_theme(key)
            parent = self.parent()
            if parent is not None:
                if hasattr(parent, 'apply_theme'):
                    parent.apply_theme(key)
                else:
                    return None
            else:
                return None
            return None
        else:
            return None
"""
assert old in s
open(p,"w",encoding="utf-8",newline="").write(s.replace(old,new))
print("patched")
