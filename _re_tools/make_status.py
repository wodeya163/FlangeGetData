import json, os

def keep(r):
    return not (r["module"].startswith("_") and r["status"] == "nopyc")

data = json.load(open(os.path.join(os.environ["TEMP"], "status.json"), encoding="utf-8-sig"))
order = ["单位换算工具", "公差查询工具V2.5", "轴承选型工具V1.0测试版", "弹设计工具V1.0测试版",
         "螺栓连接校核V5", "螺栓拧紧力矩工具V2.5", "键联接选型工具V2.3.28", "齿轮参数工具V1.0测试版", "密封圈选型工具V2.5"]
by = {d["app"]: d for d in data}
L = ["# 反编译现状（自动生成）", "",
     "判定口径：源文件用与原始 exe 相同版本的 CPython 重新编译，与 `original_pyc` 中",
     "的代码对象逐个比对（数值字面量归一化、跳转目标解析后再比对）。", "",
     "| 工具 | Python | 模块 | 完全一致 | 有差异 | 缺函数 | 语法错误 |",
     "|---|---|---|---|---|---|---|"]
tm = te = td = tmi = ts = 0
for app in order:
    rows = [r for r in by[app]["rows"] if keep(r)]
    ex = sum(1 for r in rows if r["status"] == "exact")
    df = sum(1 for r in rows if r["status"] == "diff")
    sy = sum(1 for r in rows if r["status"] == "syntax")
    ms = sum(r.get("missing", 0) for r in rows)
    tm += len(rows); te += ex; td += df; tmi += ms; ts += sy
    L.append("| %s | %s | %d | %d | %d | %d | %d |" % (app, by[app]["python"], len(rows), ex, df, ms, sy))
L += ["| **合计** | | **%d** | **%d** | **%d** | **%d** | **%d** |" % (tm, te, td, tmi, ts), ""]
names = {"exact": "完全一致", "diff": "有差异", "syntax": "语法错误",
         "nopyc": "无 pyc（随包源码）", "error": "读取失败"}
for app in order:
    L += ["## " + app, "", "| 模块 | 状态 | 代码对象 | 一致 | 差异 | 缺函数 |",
          "|---|---|---|---|---|---|"]
    for r in by[app]["rows"]:
        if not keep(r):
            continue
        L.append("| `%s` | %s | %s | %s | %s | %s |" % (
            r["module"], names.get(r["status"], r["status"]), r.get("objects", "-"),
            r.get("exact", "-"), r.get("diff", "-"), r.get("missing", "-")))
    L.append("")
open(r"_decompiled_tools\STATUS.md", "w", encoding="utf-8").write("\n".join(L))
print("total", tm, "exact", te, "diff", td, "missing", tmi, "syntax", ts)
