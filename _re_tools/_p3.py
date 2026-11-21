import re
p=r"_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py"
s=open(p,encoding="utf-8-sig").read()
def rep(a,b,n=1):
    global s
    assert a in s, a[:70]
    s=s.replace(a,b,n)
# module-level global decl
rep("""from seal_data import ORING_SIZES,""","""global BG, CARD, CARD2, BORDER, TEXT, TEXT2, ACCENT, GREEN, RED, ORANGE, BG_H, CARD_H, ACCENT_H, SEC
from seal_data import ORING_SIZES,""")
rep("""        return ('孔（衬套面）', '轴（沟槽侧）')""","""        return ('套筒（孔面）', '轴（沟槽侧）')""")
rep("""    BG_H = None
    CARD_H = None
    ACCENT_H = None""","""    BG_H = CARD_H = ACCENT_H = None""")
rep("""class OringTab:""","""class OringTab(QWidget):""")
rep("""class GrooveTab:""","""class GrooveTab(QWidget):""")
rep("""class MaterialTab:""","""class MaterialTab(QWidget):""")
rep("""class KnowledgeTab:""","""class KnowledgeTab(QWidget):""")
rep("""class MainWindow:""","""class MainWindow(QMainWindow):""")
rep("""class GrooveWidget:""","""class GrooveWidget(QWidget):""")
s2=re.sub(r"\n    __classcell__ = None","",s)
open(p,"w",encoding="utf-8",newline="").write(s2)
print("ok")
