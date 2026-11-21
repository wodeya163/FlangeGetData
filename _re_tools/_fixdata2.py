import io
p = r"_decompiled_tools\密封圈选型工具V2.5\source\seal_data.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace("    2.65: (2, 2.1, 2.15, 3.4, 3.6, 5, 6.4),", "    2.65: (2.0, 2.1, 2.15, 3.4, 3.6, 5.0, 6.4),")
s = s.replace("""        if not need:
            review.append('挤出间隙本标准未给数值限值，如间隙偏大，可结合挡圈供应商手册复核')
        else:
            factors.append(('挤出间隙', '未提供', '标准仅定义符号未给限值（第3章 g），可补充后一并复核'))""", """        if not need:
            review.append('挤出间隙本标准未给数值限值，如间隙偏大，可结合挡圈供应商手册复核')
    else:
        factors.append(('挤出间隙', '未提供', '标准仅定义符号未给限值（第3章 g），可补充后一并复核'))""")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
