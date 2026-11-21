# Reconstructed from bytecode by split_decompile.py
# personal_excel.relaxed.pyc

'''
个人扭矩库 Excel 导入/导出/模板（V2.2, openpyxl）
列结构: 螺纹类型|规格|等级或材质|来源|最小力矩(N·m)|推荐力矩(N·m)|最大力矩(N·m)|场景|备注
'''
import os
from personal_store import validate_record_row, list_records
HEADERS = [
    '螺纹类型',
    '规格',
    '等级或材质',
    '来源',
    '最小力矩(N·m)',
    '推荐力矩(N·m)',
    '最大力矩(N·m)',
    '场景',
    '备注']

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

_EXAMPLES = [
    [
        '粗牙',
        'M12',
        '10.9',
        '试验值',
        105,
        123.6,
        142.1,
        '一般连接',
        '示例-可删除'],
    [
        '细牙',
        'M12×1.5',
        '10.9',
        '工艺卡',
        '',
        130,
        '',
        '',
        'A线工位'],
    [
        '自攻',
        'ST4.2',
        'Q235薄板',
        '经验',
        '',
        3.8,
        '',
        '',
        '示例-可删除']]

def make_template(path):
    '''生成导入模板（含表头样式与 3 行示例）。'''
    if not HAS_OPENPYXL:
        raise RuntimeError('未安装 openpyxl, 无法生成模板')
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = '个人扭矩记录'
    head_fill = PatternFill('solid', fgColor = '2E3A46')
    for col, h in enumerate(HEADERS, 1):
        cell = ws.cell(row = 1, column = col, value = h)
        cell.font = Font(bold = True, color = 'FFFFFF')
        cell.fill = head_fill
        cell.alignment = Alignment(horizontal = 'center')
        ws.column_dimensions[cell.column_letter].width = 16
        for r, row in enumerate(_EXAMPLES, 2):
            for c, v in enumerate(row, 1):
                ws.cell(row = r, column = c, value = v)
                ws.freeze_panes = 'A2'
                wb.save(path)
                return path
def export_records(path):
    '''导出当前全部个人记录。返回条数。'''
    if not HAS_OPENPYXL:
        raise RuntimeError('未安装 openpyxl, 无法导出')
    rows = list_records()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = '个人扭矩记录'
    head_fill = PatternFill('solid', fgColor = '2E3A46')
    for col, h in enumerate(HEADERS, 1):
        cell = ws.cell(row = 1, column = col, value = h)
        cell.font = Font(bold = True, color = 'FFFFFF')
        cell.fill = head_fill
        cell.alignment = Alignment(horizontal = 'center')
        ws.column_dimensions[cell.column_letter].width = 16
        for r, rec in enumerate(rows, 2):
            vals = [
                rec['thread_type'],
                rec['spec'],
                rec['grade_material'],
                rec['source'],
                rec['t_min'],
                rec['t_rec'],
                rec['t_max'],
                rec['scenario'],
                rec['note']]
            for c, v in enumerate(vals, 1):
                ws.cell(row = r, column = c, value = v)
                ws.freeze_panes = 'A2'
                wb.save(path)
                return len(rows)
def parse_import(path):
    pass


def validate_all(rows):
    '''对解析出的 rows 逐行校验。返回 (ok_rows, [(行号, 错误)])。'''
    errs = []
    ok = []
    for i, raw in enumerate(rows, start = 2):
        (rec, err) = validate_record_row(raw)
        if err:
            errs.append((i, err))
            continue
        ok.append(rec)
        return (ok, errs)

