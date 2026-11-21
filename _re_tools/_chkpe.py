import sys,dis
sys.path.insert(0,r"E:\AI作品\work\FlangeGetData\_re_tools")
import verify
O=dict(verify.walk(verify.load_pyc(r"E:\AI作品\work\FlangeGetData\密封圈选型工具V2.5.exe_extracted\PYZ.pyz_extracted\seal_ui.pyc")))["GrooveWidget.paintEvent"]
N=dict(verify.walk(compile(open(r"E:\AI作品\work\FlangeGetData\_decompiled_tools\密封圈选型工具V2.5\source\seal_ui.py",encoding="utf-8").read(),"x","exec")))["GrooveWidget.paintEvent"]
oi=list(dis.get_instructions(O)); ni=list(dis.get_instructions(N))
for i in range(664,690): print("O",i,oi[i].offset,oi[i].opname,oi[i].argrepr)
print("---")
for i in range(664,690): print("N",i,ni[i].offset,ni[i].opname,ni[i].argrepr)
