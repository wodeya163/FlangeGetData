import io
p = r"_decompiled_tools\密封圈选型工具V2.5\source\theme.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace("class ThemeDialog:\n", "class ThemeDialog(QDialog):\n")
s = s.replace("    def __init__(self, parent):\n        super().__init__(parent)\n        self.setWindowTitle('外观主题')", "    def __init__(self, parent=None):\n        super().__init__(parent)\n        self.setWindowTitle('外观主题')")
s = s.replace("        t = None[key]", "        t = THEMES[key]")
s = s.replace("    a = lum(hex1)\n    b = lum(hex2)\n    hi = max(a, b)\n    lo = min(a, b)", "    a, b = lum(hex1), lum(hex2)\n    hi, lo = max(a, b), min(a, b)")
s = s.replace("    __classcell__ = None\n", "")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
