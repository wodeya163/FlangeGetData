# -*- coding: utf-8 -*-
"""导出相关的纯函数，便于在不启动 GUI 的情况下做单元测试。"""

import csv
import math
import zipfile


def resolve_export_columns(rows, visible_cols=None, fallback_cols=None):
    """按“当前表格可见列优先、回退列兜底”的顺序确定导出列。

    这样钢管壁厚、波纹管几何参数、垫片 PN/Class 等页面特有列不会因为
    共用 SHOW_COLS 而被漏掉。
    """
    if not rows:
        return []
    available = set(rows[0].keys())
    cols = []
    for col in visible_cols or []:
        if col in available and col not in cols:
            cols.append(col)
    if cols:
        return cols
    for col in fallback_cols or []:
        if col in available and col not in cols:
            cols.append(col)
    return cols


def write_csv(path, rows, cols):
    """写出 utf-8-sig CSV，Excel 直接打开不乱码。"""
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        for row in rows:
            writer.writerow([row.get(col, '') for col in cols])


def rows_to_tsv(rows, cols):
    """生成可粘贴到 Excel 的 TSV 文本。"""
    def cell(value):
        return (str('' if value is None else value)
                .replace('\t', ' ').replace('\r', ' ').replace('\n', ' '))

    lines = ['\t'.join(cell(col) for col in cols)]
    for row in rows:
        lines.append('\t'.join(cell(row.get(col, '')) for col in cols))
    return '\n'.join(lines) + '\n'


def _xml_escape(text):
    text = ''.join(ch for ch in str(text)
                   if ch in '\t\n\r' or ord(ch) >= 32)
    return (text.replace('&', '&amp;').replace('<', '&lt;')
                .replace('>', '&gt;').replace('"', '&quot;'))


def _col_letter(index):
    letters = ''
    while index > 0:
        index, rem = divmod(index - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def _number_text(value):
    text = str(value).strip()
    if text in ('', '-'):
        return None
    try:
        number = float(text.replace(',', '.'))
    except ValueError:
        return None
    if not math.isfinite(number):
        return None
    if number == int(number):
        return str(int(number))
    return repr(number)


def _sheet_name(name):
    for ch in '[]:*?/\\':
        name = name.replace(ch, '_')
    return (name or 'Sheet1')[:31]


_CONTENT_TYPES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''

_ROOT_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''

_CORE = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:creator>FlangeQuery</dc:creator><cp:lastModifiedBy>FlangeQuery</cp:lastModifiedBy>
</cp:coreProperties>'''

_APP = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>FlangeQuery</Application></Properties>'''

_STYLES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>
<fills count="1"><fill><patternFill patternType="none"/></fill></fills>
<borders count="1"><border/></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''


def write_xlsx(path, rows, cols, sheet_name='查询结果'):
    """写一个无第三方依赖的最小 XLSX 工作簿（单 sheet，首行表头）。"""
    all_rows = [list(cols)]
    all_rows += [[row.get(col, '') for col in cols] for row in rows]

    sheet_rows = []
    for r_index, values in enumerate(all_rows, start=1):
        cells = []
        for c_index, value in enumerate(values, start=1):
            ref = '%s%d' % (_col_letter(c_index), r_index)
            text = '' if value is None else str(value)
            number = _number_text(text) if r_index > 1 else None
            if number is not None:
                cells.append('<c r="%s"><v>%s</v></c>' % (ref, number))
            else:
                cells.append(
                    '<c r="%s" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>'
                    % (ref, _xml_escape(text)))
        sheet_rows.append('<row r="%d">%s</row>' % (r_index, ''.join(cells)))

    sheet = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
             '<dimension ref="A1:%s%d"/><sheetData>%s</sheetData></worksheet>'
             % (_col_letter(max(1, len(cols))), max(1, len(all_rows)),
                ''.join(sheet_rows)))
    workbook = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                '<sheets><sheet name="%s" sheetId="1" r:id="rId1"/></sheets></workbook>'
                % _xml_escape(_sheet_name(sheet_name)))
    workbook_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                     '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
                     '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                     '</Relationships>')

    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', _CONTENT_TYPES)
        zf.writestr('_rels/.rels', _ROOT_RELS)
        zf.writestr('docProps/core.xml', _CORE)
        zf.writestr('docProps/app.xml', _APP)
        zf.writestr('xl/workbook.xml', workbook)
        zf.writestr('xl/_rels/workbook.xml.rels', workbook_rels)
        zf.writestr('xl/styles.xml', _STYLES)
        zf.writestr('xl/worksheets/sheet1.xml', sheet)
