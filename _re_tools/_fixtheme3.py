import io
p = r"_decompiled_tools\密封圈选型工具V2.5\source\theme.py"
s = io.open(p, encoding="utf-8").read()
old = """        if key != current_name():
            self.setStyleSheet(qss(t, for_dialog=True))
            set_theme(key)
            parent = self.parent()
            if parent is not None or hasattr(parent, 'apply_theme'):
                parent.apply_theme(key)
                return None
            return None
        return None"""
new = """        if key != current_name():
            self.setStyleSheet(qss(t, for_dialog=True))
            set_theme(key)
            parent = self.parent()
            if parent is not None:
                if hasattr(parent, 'apply_theme'):
                    parent.apply_theme(key)
                    return None
                return None
            return None
        return None"""
assert old in s
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
