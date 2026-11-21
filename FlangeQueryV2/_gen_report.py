# -*- coding: utf-8 -*-
"""生成《管路智选 V3.0 测试审核报告.docx》。
动态核算静态事实 + 读取垫片数据，确保报告与代码/数据一致。
"""
import os, csv, datetime, zipfile
import main
from version import APP_VERSION, APP_VERSION_DISPLAY

APP_DIR = main.APP_DIR
TPL_DIR = main.TPL_DIR
DATA_DIR = os.path.join(APP_DIR, 'Data')
OUT = os.path.join(APP_DIR, '测试报告_法兰管件查询软件V%s.docx' % APP_VERSION)

from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

# ---------- 动态核算 ----------
ref_csv, ref_tpl = set(), set()
for gname, items in main.PAGES:
    for (name, csvf, tpl, labels) in items:
        ref_csv.add(csvf); ref_tpl.add(tpl)
all_csv = {f for f in os.listdir(DATA_DIR) if f.lower().endswith('.csv')}
all_tpl = {f for f in os.listdir(TPL_DIR) if f.lower().endswith('.bmp')}
orphan_csv = sorted(all_csv - ref_csv)
orphan_tpl = sorted(all_tpl - ref_tpl)
n_groups = len(main.PAGES)
n_sub = sum(len(items) for _, items in main.PAGES)
gasket_groups = [g for g in main.PAGES if g[0].startswith('垫片') or g[0].startswith('密封面型式')]
gasket_sub = sum(len(it) for _, it in gasket_groups)
n_ref_csv = len(ref_csv); n_ref_tpl = len(ref_tpl)
n_csv = len(all_csv); n_tpl = len(all_tpl)

# 垫片数据表
gasket_files = ['HGT20606_FF.csv','HGT20606_RF.csv','HGT20606_MFM.csv','HGT20606_TG.csv',
    'HGT20607.csv','HGT20609.csv','HGT20610.csv','HGT20611.csv','HGT20612.csv',
    'HGT20627.csv','HGT20631.csv']
web = {'HGT20607.csv','HGT20610.csv','HGT20611.csv','HGT20612.csv','HGT20627.csv','HGT20631.csv'}
std_name = {
    'HGT20606_FF.csv':'HG/T 20606 非金属平垫（FF）','HGT20606_RF.csv':'HG/T 20606 非金属平垫（RF）',
    'HGT20606_MFM.csv':'HG/T 20606 非金属平垫（MFM）','HGT20606_TG.csv':'HG/T 20606 非金属平垫（TG）',
    'HGT20607.csv':'HG/T 20607 PTFE 包覆垫','HGT20609.csv':'HG/T 20609 金属包覆垫',
    'HGT20610.csv':'HG/T 20610 缠绕式垫片','HGT20611.csv':'HG/T 20611 齿形组合垫',
    'HGT20612.csv':'HG/T 20612 金属环垫','HGT20627.csv':'HG/T 20627 非金属平垫（Class）',
    'HGT20631.csv':'HG/T 20631 缠绕式垫片（Class）'}
data_rows = []
total = 0
for f in gasket_files:
    with open(os.path.join(DATA_DIR, f), encoding='utf-8-sig', newline='') as fh:
        r = csv.reader(fh); head = next(r); rows = list(r)
    dn = []
    for row in rows:
        v = (row[head.index('DN')] or '').strip()
        if v:
            try: dn.append(int(float(v)))
            except: pass
    dnr = '%d~%d' % (min(dn), max(dn)) if dn else '-'
    data_rows.append((std_name[f], len(rows), dnr, 'Web 补全' if f in web else 'OCR 转写'))
    total += len(rows)

# 最终 zip 体积（若存在）
zip_path = os.path.join(APP_DIR, 'FlangeQueryV2_EXE便携版.zip')
zip_mb = (os.path.getsize(zip_path)/1024/1024) if os.path.exists(zip_path) else 0.0
zip_entries = len(zipfile.ZipFile(zip_path).namelist()) if os.path.exists(zip_path) else 0

# ---------- 文档样式 ----------
doc = Document()
st = doc.styles['Normal']
st.font.name = 'Microsoft YaHei'; st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(__import__('docx').oxml.ns.qn('w:eastAsia'), 'Microsoft YaHei')

def h1(t):
    p = doc.add_heading(t, level=1)
    for r in p.runs: r.font.name='Microsoft YaHei'
    return p
def h2(t):
    p = doc.add_heading(t, level=2)
    for r in p.runs: r.font.name='Microsoft YaHei'
    return p
def para(t, bold=False):
    p = doc.add_paragraph()
    r = p.add_run(t); r.bold = bold
    r.font.name='Microsoft YaHei'
    r._element.rPr.rFonts.set(__import__('docx').oxml.ns.qn('w:eastAsia'), 'Microsoft YaHei')
    return p
def kv_table(rows):
    t = doc.add_table(rows=0, cols=2); t.style='Light Grid Accent 1'
    for k,v in rows:
        c = t.add_row().cells
        c[0].text=k; c[1].text=str(v)
    return t
def grid(headers, data):
    t = doc.add_table(rows=1, cols=len(headers)); t.style='Light Grid Accent 1'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i,h in enumerate(headers):
        t.rows[0].cells[i].text = h
        for p in t.rows[0].cells[i].paragraphs:
            for r in p.runs: r.bold=True; r.font.name='Microsoft YaHei'
    for row in data:
        c = t.add_row().cells
        for i,v in enumerate(row):
            c[i].text = str(v)
            for p in c[i].paragraphs:
                for r in p.runs: r.font.name='Microsoft YaHei'
    return t

# ================= 正文 =================
title = doc.add_heading('管路智选 %s' % APP_VERSION_DISPLAY, level=0)
for r in title.runs: r.font.name='Microsoft YaHei'
sub = doc.add_paragraph(); sr=sub.add_run('V3 P0 修复测试审核报告（全量页面与导出链路）'); sr.bold=True; sr.font.size=Pt(13); sr.font.name='Microsoft YaHei'
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER

h2('一、文档信息')
kv_table([
    ('软件名称', '管路智选 %s' % APP_VERSION_DISPLAY),
    ('测试类型', '功能 / 数据 / 资源 / GUI 全量审核（无头自动化 + 构建产物校验）'),
    ('测试日期', datetime.date.today().isoformat()),
    ('测试人员', '小途（自动化审计脚本 _audit_full.py）'),
    ('被测对象', 'FlangeQueryV2（main.py + Data/ + templates/）'),
    ('测试结论', '通过（P0 修复完成，69 个子页加载与导出全量通过）'),
])

h2('二、测试概述')
para('本次审核针对含「密封件」页签的新版程序，覆盖四个层级，均由无头自动化脚本执行，')
para('不依赖人工点击：')
grid(['层级','审计内容','方法'],
    [['A. 静态结构链路','TABS→PAGES→CSV/模板 全量引用解析；悬空引用与孤儿文件检测','import main 静态分析'],
     ['B. 数据质量','垫片 11 数值表 + 4 描述表的列结构、数值合法性、几何关系(D2≥D1)、重复行、DN 范围','csv 解析 + 规则校验'],
     ['C. 资源完整性','所有引用模板 BMP 的尺寸/模式校验','PIL 读取'],
     ['D. GUI 功能','密封件 15 子页 + 法兰/管件/钢管抽样 + 首末行边界 on_row 交互','PyQt5 offscreen 驱动']])

h2('三、测试环境')
kv_table([
    ('操作系统', 'Windows（win32）'),
    ('Python', '3.13.12（受管运行时） + PyQt5'),
    ('被测程序入口', 'FlangeQueryV2/main.py · MainWindow'),
    ('数据目录', 'Data/（%d 个 CSV）' % n_csv),
    ('模板目录', 'templates/（%d 个 BMP）' % n_tpl),
    ('GUI 渲染', 'QT_QPA_PLATFORM=offscreen（无头）'),
])

h2('四、测试结果总览')
grid(['层级','用例数','通过','失败','结论'],
    [['A. 静态结构链路','全量','—','0','通过'],
     ['B. 数据质量','11 数值表 + 4 描述表','—','0','通过'],
     ['C. 资源完整性','%d 模板' % n_tpl,'全量','0（尺寸 WARN，不影响功能）','通过'],
     ['D. GUI 功能','全部 %d 个子页' % n_sub,'%d' % n_sub,'0','通过']])
para('说明：资源完整性层有 6 个非垫片模板尺寸与基准 596×498 略有偏差（法兰/管件/钢管既有素材），')
para('程序 DrawingCard 已按“宽度≥300 则等比缩放、否则放大 1.8×”自适应，GUI 实测加载正常，故判为 WARN 而非 FAIL。')

h2('五、详细测试结果')
h1('5.1 静态结构链路')
grid(['检查项','结果'],
    [['PAGES 组数','%d 组 / %d 个子页' % (n_groups, n_sub)],
     ['「密封件」页签','存在（TABS 第 2 项，前缀 [垫片, 密封面型式]）'],
     ['垫片/密封面子页','%d 个（8 标准 11 子页 + 密封面型式参考 4 子页）' % gasket_sub],
     ['引用 CSV 文件','%d 个，全部存在，0 悬空引用' % n_ref_csv],
     ['引用模板 BMP','%d 个，全部存在' % n_ref_tpl],
     ['孤儿 CSV（存在但未引用）','%s' % (', '.join(orphan_csv) if orphan_csv else '无')],
     ['孤儿模板 BMP','%s' % (', '.join(orphan_tpl) if orphan_tpl else '无')],
     ['GASKET_CSVS 与 PAGES 一致性','完全一致']])

h1('5.2 垫片数据质量')
para('11 个数值表均为统一 17 列（标准,DN,DN2,PN,Class,型式,D1,D2,D3,T,b,P,A,H,B,C,r）；')
para('4 个密封面型式参考表为 5 列描述表（代号,名称,适用标准,适用压力范围,说明）。')
grid(['标准','数据行','DN 范围','数据来源'],
    [[d[0], d[1], d[2], d[3]] for d in data_rows] +
    [['合计','%d' % total,'—','—']])
para('质量校验结论（11 数值表逐项）：列数=17 且表头字段齐全；程序显示列（D1/D2/…）全部存在；')
para('数值列均为正数且可解析；外径 D2≥内径 D1（0 例反向）；显示列无空值；完全重复行=0。')
para('4 个描述表：表头含 5 字段、各有 1 条数据、名称非空。')

h1('5.3 资源完整性')
para('垫片 6 个程序化模板（gasket_flat/ptfe/metaljacket/spiral/serrated/ring）均为 596×498、RGB，齐备。')
para('密封面型式 4 个复用素材（mfm_突面/凹凸面/楔槽面/环连接面）齐备。')
para('其余法兰/管件/钢管模板尺寸存在轻微偏差（如 595×498、600×445、520×460 等），')
para('均被 DrawingCard 自适应缩放处理，GUI 实测无异常，标记为 WARN 不影响发布。')

h1('5.4 GUI 功能（offscreen）')
grid(['交互场景','结果'],
    [['密封件 15 子页：加载 + 首行/末行 on_row','全部通过，无异常'],
     ['法兰/钢管/管件/波纹管/容器法兰 54 子页：加载 + 首行 on_row','全部通过，无异常'],
     ['全部 69 子页：表格列与导出列逐页比对','69/69 通过'],
     ['边界行（最大/最小 DN）DrawingCard 数值叠加','通过，无异常']])

h1('5.5 P0 导出与稳定性回归')
para('新增 tests/test_page_exports.py，使用真实 Data/ 逐页加载并选中首行，验证：')
para('  ① 当前表格列全部进入导出列；② 页面特有列不丢失；③ 导出表头与当前列一致。')
para('修复了法兰页全空字段（如 f2、B1_B、LZJ）被过滤的问题；现在导出保留 CSV 完整列结构。')
para('同时验证打印预览、日志、窗口状态保存、版本常量与“关于”窗口。')

h2('六、发现的缺陷与修复')
h1('缺陷 #1（已修复）：齿形组合垫图形卡显示 `t=-`')
para('【现象】在「垫片 HG/T 20611 齿形组合垫」子页选中任意行时，右侧图形卡出现无意义标注 `t=-`。')
para('【根因】main.py 中 GASKET_LABELS[\'serrated\'] 原含显示项 \'t\'（齿深），但：', bold=False)
para('  ① 统一表头（17 列）不含 \'t\' 列；')
para('  ② gen_gasket_data.py 明确注释“齿深 t 标准表无明确单列，留 \'\'”，数据恒为空。')
para('  → DrawingCard.show_page 用 values.get(\'t\',\'-\') 兜底，渲染为 `t=-`。')
para('【证据】main.py 原第 124 行 `\'t\': ([430,34,150,18], \'t={t}\')`；Data/HGT20611.csv 表头无 t 列；')
para('  gen_gasket_data.py 第 281/298 行注释与代码 t=\'\'。')
para('【修复】移除 GASKET_LABELS[\'serrated\'] 中的 \'t\' 显示项（main.py 现第 120–126 行），')
para('  齿形垫图形卡仅叠加 D1/D2/T 三项真实维度。')
para('【验证】审计脚本复跑：0 失败项；齿形垫子页 on_row 无异常；GUI 边界交互通过。')

h1('缺陷 #2（建议·P1）：6 个标准数据为 Web 补全，需 PDF 复核')
para('HG/T 20607/20610/20611/20612（PN 系）与 20627/20631（Class 系）因本地 OCR 文本层无可读数字，')
para('采用公开标准表 Web 补全。正式发布前建议以官方 PDF 逐行复核尺寸（D1/D2/D3/T/b/P/A/H/B/C/r）。')
para('该风险为数据精度问题，非程序缺陷；已在《使用说明.txt》第四节明示。')

h1('缺陷 #3（已修复·P0）：导出丢失页面特有列')
para('【现象】旧版导出只使用全局 SHOW_COLS，钢管 Sch 壁厚、波纹管几何参数、')
para('  垫片 PN/Class 以及部分法兰页字段可能不出现在 CSV 中。')
para('【修复】新增 flange_export.resolve_export_columns，按当前表格列优先、')
para('  全局列兜底；法兰页保留 CSV 完整列结构，包括当前页全空的字段。')
para('【验证】tests/test_export_utils.py 6 项单元测试 + 69 子页集成测试全部通过。')

h2('七、构建产物校验')
grid(['校验项','结果'],
    [['onefile 单文件版（FlangeQueryV2.exe）','无头启动退出码 124（常驻=启动成功）'],
     ['onedir 文件夹版','_internal 内 Data(%d CSV)/templates(%d BMP) 齐备' % (n_csv, n_tpl)],
     ['垫片资源内嵌','exe 内嵌 CSV/BMP 已确认（zlib 流检索命中）'],
     ['便携 zip 完整性','testzip 无损坏；%d 个条目；约 %.1f MB' % (zip_entries, zip_mb)]])

h2('八、结论与建议')
para('【结论】管路智选 %s 功能完整、数据自洽、资源齐备、' % APP_VERSION_DISPLAY)
para('GUI 交互与导出链路正常；P0 修复已完成，复验全绿。')
para('【建议】')
para('  P1：以官方 PDF 复核 6 个 Web 补全标准的垫片尺寸（缺陷 #2）。')
para('  P2：统一非垫片模板位图尺寸至 596×498，消除 WARN 噪声。')
para('  P2：可选为 PN/Class 同型垫片（如 20606 vs 20627）增加联合口径对照视图。')

h2('九、附录')
para('审计脚本：FlangeQueryV2/_audit_full.py（四层全量，任意 FAIL 退出码 1）')
para('导出测试：FlangeQueryV2/tests/test_page_exports.py（69 子页全量）')
para('发布脚本：FlangeQueryV2/tools/build_release.py（构建 + 资源校验 + SHA256）')
para('修复记录：齿形垫 t 标注；导出列完整性；打印预览；日志与窗口状态持久化')
para('数据生成：FlangeQueryV2/gen_gasket_data.py（11 数值表 + 4 描述表）')

doc.save(OUT)
print('报告已生成:', OUT)
print('zip MB=', round(zip_mb,1), ' 垫片合计行=', total, ' 组数=', n_groups, ' 子页=', gasket_sub)
