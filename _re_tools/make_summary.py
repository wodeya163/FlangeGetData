import json, os
data = json.load(open(os.path.join(os.environ["TEMP"], "status.json"), encoding="utf-8-sig"))
order = ["单位换算工具", "公差查询工具V2.5", "轴承选型工具V1.0测试版", "弹设计工具V1.0测试版",
         "螺栓连接校核V5", "螺栓拧紧力矩工具V2.5", "键联接选型工具V2.3.28", "齿轮参数工具V1.0测试版", "密封圈选型工具V2.5"]
by = {d["app"]: d for d in data}
def keep(r):
    return not (r["module"].startswith("_") and r["status"] == "nopyc")
out = {"toolchain": {"unpacker": "pyinstxtractor-ng", "decompiler": "pycdc (Decompyle++)",
                      "verifier": "_re_tools/verify.py (bytecode-exact, lenient mode)",
                      "recovery": "_re_tools/{isolate,stub,resync}.py"},
       "criteria": "source recompiled with the same CPython version, code objects compared instruction by instruction",
       "totals": {}, "apps": []}
tm = te = td = tmi = ts = 0
for app in order:
    rows = [r for r in by[app]["rows"] if keep(r)]
    ex = sum(1 for r in rows if r["status"] == "exact")
    df = sum(1 for r in rows if r["status"] == "diff")
    sy = sum(1 for r in rows if r["status"] == "syntax")
    ms = sum(r.get("missing", 0) for r in rows)
    tm += len(rows); te += ex; td += df; tmi += ms; ts += sy
    out["apps"].append({"app": app, "python": by[app]["python"], "modules": len(rows),
                        "exact": ex, "with_differences": df, "syntax_errors": sy,
                        "missing_code_objects": ms,
                        "modules_detail": rows})
out["totals"] = {"apps": len(order), "modules": tm, "bytecode_exact": te,
                 "with_differences": td, "syntax_errors": ts, "missing_code_objects": tmi}
json.dump(out, open(r"_decompiled_tools\summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(out["totals"])
