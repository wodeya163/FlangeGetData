# 管路智选 V3.78.4

<img src="app_icon.png" width="72" align="right" alt="管路智选图标">

基于 PyQt5 的离线管路规格查询与机械选型工具：覆盖法兰、垫片、钢管、管件、波纹管、容器法兰、重量计算，以及齿轮、单位、弹簧、公差、键、螺栓、拧紧力矩和轴承选型。程序不依赖网络，启动后直接读取内置 CSV 与模板图片。

## 快速开始

推荐直接运行打包版：

```text
dist\FlangeQueryV2.exe                         # 单文件版
dist\FlangeQueryV2\FlangeQueryV2.exe           # 文件夹版，启动更快
```

源码运行：

```bat
python -m pip install -r requirements.txt
python main.py
```

也可以双击 `启动管路智选.bat`。脚本会依次尝试项目内 `.venv`、PATH 中的 `python`、`py -3`，确认 PyQt5 可用后再启动。

## 功能概览

- 重量计算新增“金属材料”页：板材、圆棒、方棒、六角棒、圆管、方管、角钢、槽钢、工字钢；
- 金属材料数据与公式移植自开源项目 [metal-material-calculator](https://github.com/gdjoss/metal-material-calculator)（main 分支 commit `276b722`）；

- 8 个分类页签：法兰、密封件、管件、钢管、波纹管、容器法兰、重量计算、选型工具。
- 18 个标准分组、86 个子页；覆盖 GB/T、HG/T、NB/T、ASME 钢管及 GB/T 12459 管件。
- 重量计算：直管/弯头/三通，参数手动输入；直管/弯头结果上方显示矢量示意图，右侧显示质量、体积和公式。
- 选型工具：齿轮、单位换算、弹簧设计、公差、键联接、螺栓校核、拧紧力矩、轴承；8 个工具均已接入：单位换算、公差查询、键联接、螺栓拧紧力矩、螺栓连接校核、轴承选型、齿轮参数、弹簧设计。
- 左侧标准树搜索、动态筛选、表格排序和行选中联动。
- 右侧矢量图与尺寸标注、键值尺寸列表。\n- 行级复核状态：表格首列显示状态与颜色，选中行显示本行来源；\n- 面型尺寸缺失时图形标“近似”，并给出缺口清单。
- 打印预览：按纸张大小自适应缩放图形卡和尺寸表。\n- 顶栏「矢量图」：法兰/管件/垫片/钢管/波纹管/密封面可导出 PDF、SVG 参数化矢量图；\n- 管件页可选择 Sch 壁厚系列，按 GB/T 12459 壁厚表逐规格取壁厚；打印预览在有 spec 的页面使用矢量绘制。
- CSV 导出：优先使用当前表格的完整列结构，保留钢管 Sch 列、垫片 PN/Class、波纹管几何参数等页面特有字段。
- 窗口位置和上次页签自动保存；未处理异常写入日志并弹出提示。

## 数据与资源

- `Data/`：58 份 CSV，应用内置数据源。
- `Data/data.db`、`Data/manifest.json`：构建时由 `python tools\build_data.py` 生成（CSV 仍是编辑源）。
- `templates/`：29 份在用 BMP 图形模板（另有 5 份未引用模板归档在仓库根目录 `_archive/unused_templates/`）。
- `version.py`：版本号的唯一来源，界面、日志和发布脚本统一读取。
- `flange_export.py`：导出列选择与 CSV 写入逻辑的纯函数实现。

数据校核说明：

- HG/T 20607、20610、20611、20612、20627、20631 为公开标准表补全，正式对外发布前应以官方 PDF 逐项复核。
- HG/T 20627 当前仅收录 Class 150/300/600。
- GB/T 9124.1/9124.2 复用 HG/T 20592/20615 的衔接尺寸，不等同于逐条扫描国标原文。
- 本版本没有修改任何数据值；上述事项属于 P1 数据治理范围。

## 目录结构

```text
FlangeQueryV2/
  main.py                 主界面、查询、筛选、打印与导出
  flange_export.py        导出列选择、UTF-8-SIG CSV 写入
  version.py              应用名称与版本
  Data/                   内置 CSV
  drawspec/               DrawingSpec、尺寸布局、PDF/SVG 渲染\n  templates/              内置 BMP
  tests/                  单元测试与 GUI 集成测试
  tools/build_release.py  构建、打包、校验与 SHA256 生成
  dist/                   构建产物（不纳入版本库）
```

## 测试

纯逻辑测试不需要 GUI：

```bat
python -m unittest discover -s tests -v
```

现有回归脚本会检查真实数据与无头界面：

```bat
set QT_QPA_PLATFORM=offscreen
set PYTHONIOENCODING=utf-8
python _smoke.py
python _smoke_pipe.py
python _smoke_bellows.py
python _audit_full.py
```

`tests/test_page_exports.py` 会遍历全部 86 个子页，验证：

- 每页均能加载数据；
- 表格选中首行后能得到有效尺寸；
- 当前表格列完整进入导出列；
- 导出的表头与当前列一致。

同一集成测试还会把法兰页和波纹管页渲染为 PDF，验证打印预览链路。

如果运行环境没有 PyQt5，该集成测试会自动跳过。

## 构建与发布

安装构建依赖后执行：

```bat
python -m pip install -r requirements-build.txt
python tools\build_release.py --clean
```

脚本会依次完成：

1. 运行语法检查和单元测试；
2. 清理并构建单文件版、文件夹版；
3. 按 `docs\使用说明模板.txt` 生成便携包使用说明（自动注入版本、构建日期、CSV/模板数量）；
4. 组装便携 zip，校验内置 CSV、模板和 zip 完整性；
5. 生成 `dist\FlangeQueryV2-<版本>.sha256`（版本取自 `version.py`）与便携包 SHA256。

使用说明由模板生成，发版前只需改 `docs\使用说明模板.txt`，不必手改 `_打包\使用说明.txt`。

可选安装包（需安装 Inno Setup 6）：

```bat
python tools\build_installer.py
:: 或随主构建一起执行
python tools\build_release.py --clean --installer
```

安装包输出到 `dist\installer\FlangeQueryV2-<版本>-setup.exe`。如配置了 `SIGNTOOL`（signtool.exe 路径）与 `CERT_PATH`（pfx 路径），构建脚本会先签 exe、再签安装包；未配置则跳过签名。两个 spec 已关闭 UPX，避免杀软误报。

发布前应在目标机器上手动启动 exe，检查打印预览、导出和中文显示。当前构建未做代码签名，Windows SmartScreen 可能提示未知发布者；如需签名，应在构建后使用单位代码签名证书处理。

## 日志与设置

- 日志：`%LOCALAPPDATA%\FlangeQuery\logs\FlangeQuery.log`，单文件 1 MB，保留 3 份。
- 设置：`HKEY_CURRENT_USER\Software\FlangeQuery\FlangeQueryV3`，仅保存窗口几何和当前页签。
- 关于窗口：显示版本、页面统计、数据目录和日志路径。

## 键联接选型对齐

键联接选型工具已按 `键联接选型工具V2.3.28.exe` 的页签、键型、参数、校核和示意图逐步对齐，并保留浅色主题。  
详细功能对照、标准、验证记录和有意保留的差异见：

```text
docs/键选型对齐清单.md
```

## 齿轮 STP 生成

齿轮工具的 STP 页使用 CadQuery 2.8.0 + OCP 7.9.3.1.1 生成直齿/斜齿圆柱齿轮 STEP。  
OCP 轮子不支持 Python 3.13，因此 CadQuery 安装在独立 Python 3.12 环境：

```text
_cadquery_env\Scripts\python.exe
```

源码运行时会自动查找该环境。便携版或移动目录后，可设置：

```text
FLANGE_CADQUERY_PYTHON=<CadQuery 环境的 python.exe>
```

STP 页支持模数、齿数、齿宽、轴孔、压力角、螺旋角、变位系数、齿顶高系数和顶隙系数。

## 已知限制

- 图形模板使用固定像素坐标叠加标注，部分页面仍沿用原程序坐标，后续可逐页精修。
- 单文件版首次启动需要解压，速度慢于文件夹版。
- 已支持半自动更新（GitHub Releases 源，仅文件夹版）：启动静默检查，「关于」框可手动检查，确认后下载 + SHA256 校验 + 覆盖重启。单文件版不支持自更新。
- 暂无代码签名，Windows SmartScreen 可能提示未知发布者；分发以便携文件夹版为主。
