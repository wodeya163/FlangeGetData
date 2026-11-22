# -*- coding: utf-8 -*-
"""数据来源、复核状态与标准覆盖矩阵（无 Qt 依赖）。"""

# GB/T 9124 页签目前复用 HG/T 尺寸表，必须在界面、打印与导出中显式标注来源
PROVENANCE = {
    'GB/T 9124.1-2019（PN 系列·欧洲体系）':
        '数据源：GB/T 9124.1-2019 表6、表8–91。WN 209 行逐项复核（修正 31 处 N 系列Ⅱ）；'
        '其余 8 类按 PDF 重建专用数据表，公共尺寸逐项复核',
    'GB/T 9124.2-2019（Class 系列·美洲体系）':
        '数据源：GB/T 9124.2-2019 PDF（扫描件，目视抽样复核 Class150 共 30 规格 / 223 字段全部一致；'
        '全量其他 Class 未逐条核对）',
}


def source_note(std, csvf=''):
    if csvf.startswith('GBT9124_1_带颈对焊'):
        return '数据源：GB/T 9124.1-2019 表27–38（PN2.5–400，DN≤600，已逐项复核）'
    if csvf.startswith('GBT9124_1_'):
        return '数据源：GB/T 9124.1-2019 PDF 表6、表8–91 逐项复核（公共尺寸按 PDF 重建）'
    if csvf.startswith('GBT9124_2_带颈对焊'):
        return '数据源：GB/T 9124.2-2019 表19–24（Class150–2500）'
    if csvf.startswith('GBT9124_2_带颈平焊'):
        return '数据源：GB/T 9124.2-2019 表25–29（SO Class150–1500）'
    if csvf.startswith('GBT9124_2_整体'):
        return '数据源：GB/T 9124.2-2019 表7–12（IF Class150–2500）'
    if csvf.startswith('GBT9124_2_承插焊'):
        return '数据源：GB/T 9124.2-2019 表30–33（SW Class150–1500）'
    if csvf.startswith('GBT9124_2_螺纹'):
        return '数据源：GB/T 9124.2-2019 表13–18（Th Class150–2500）'
    if csvf.startswith('GBT9124_2_法兰盖'):
        return '数据源：GB/T 9124.2-2019 表40–45（BL Class150–2500）'
    return PROVENANCE.get(std, '')


def attach_source(rows, note):
    """导出时附加“数据来源”列，始终返回副本，不修改原行对象。"""
    out = [dict(r) for r in rows]
    if note:
        for row in out:
            row.setdefault('数据来源', note)
    return out


REVIEW_LABELS = {
    'verified': '已核对',
    'partial': '部分核对',
    'inferred': '推断/补全',
    'alias': '来源待复核',
    'descriptive': '说明性数据',
    'missing': '未收录',
    'unknown': '未标注',
}

# 每个数据族的来源与复核状态（按 CSV 前缀匹配）
DATA_REVIEW = (
    ('GB17395_', 'verified', 'GB/T 17395-2024 PDF 全文录入'),
    ('HGT20592_', 'partial', '原程序 CSV，未逐条核对 HG/T 20592 PDF'),
    ('HGT20615_', 'partial', '原程序 CSV，未逐条核对 HG/T 20615 PDF'),
    ('HGT20623_', 'partial', '原程序 CSV，未逐条核对 HG/T 20623 PDF'),
    ('NBT47023', 'partial', '原程序 CSV，未逐条核对 NB/T 47023'),
    ('ANSIB36', 'partial', 'ASME B36.10M/19M 公开表转写'),
    ('HGJ514', 'partial', '老标准，来源未归档'),
    ('HGJ528', 'partial', '老标准，来源未归档'),
    ('HG20553', 'partial', '来源未归档'),
    ('GB12459_', 'partial', 'GB/T 12459/13401 标准表转写'),
    ('U_bellows', 'partial', '70B125-2002 表A.1，原件缺失'),
    ('HGT20606', 'partial', '干净 OCR 转写'),
    ('HGT20609', 'partial', '干净 OCR 转写'),
    ('HGT20607', 'inferred', '公开标准表补全'),
    ('HGT20610', 'inferred', '公开标准表补全'),
    ('HGT20611', 'inferred', '公开标准表补全'),
    ('HGT20612', 'inferred', '公开标准表补全'),
    ('HGT20627', 'partial', 'PDF 抽样 D1/D2/T 一致；仅 Class 150/300/600'),
    ('HGT20631', 'inferred', '公开标准表补全'),
    ('mfm_', 'descriptive', '密封面型式说明，非尺寸表'),
)


def review_for(csvf, std=''):
    """返回某数据文件的来源与复核状态。"""
    if csvf.startswith('GBT9124_1_带颈对焊'):
        return {'status': 'verified', 'label': REVIEW_LABELS['verified'],
                'source': 'GB/T 9124.1-2019 表27–38 逐项复核（209 行，已修正 31 处 N 系列Ⅱ）'}
    if csvf.startswith('GBT9124_1_'):
        fam = csvf[len('GBT9124_1_'):].split('.')[0]
        notes = {
            '整体': ('表8–19', 'IF 整体法兰'),
            '螺纹': ('表20–26', 'Th 带颈螺纹法兰'),
            '带颈平焊': ('表39–45', 'SO 带颈平焊法兰'),
            '承插焊': ('表46–49', 'SW 带颈承插焊法兰'),
            '板式平焊': ('表50–57', 'PL 板式平焊法兰'),
            '对焊环松套': ('表58–67', 'PJSE 对焊环板式松套法兰'),
            '平焊环松套': ('表68–73', 'PJRJ 平焊环板式松套法兰'),
            '法兰盖': ('表80–91', 'BL 钢制管法兰盖'),
        }
        tables, desc = notes.get(fam, ('表8–91', fam))
        return {'status': 'verified', 'label': REVIEW_LABELS['verified'],
                'source': 'GB/T 9124.1-2019 %s %s，公共尺寸按 PDF 逐项复核；'
                          '密封面 d/f1 取表6，质量等非尺寸列沿用 HG/T 参考值'
                          % (tables, desc)}
    if csvf.startswith('GBT9124_2_'):
        fam = csvf[len('GBT9124_2_'):].split('.')[0]
        tables = {
            '带颈对焊': '表19–24', '带颈平焊': '表25–29', '整体': '表7–12',
            '承插焊': '表30–33', '螺纹': '表13–18', '法兰盖': '表40–45',
        }.get(fam, '表7–45')
        return {'status': 'partial', 'label': REVIEW_LABELS['partial'],
                'source': 'GB/T 9124.2-2019 %s PDF 转录；扫描件目视抽样复核'
                          '（Class150 代表表共 30 规格 223 字段一致），'
                          '其余 Class 未逐条核对' % tables}
    if std.startswith('GB/T 9124'):
        if '9124.1' in std:
            note = ('PN 系列 9 类法兰均已按 GB/T 9124.1-2019 PDF 复核；'
                    '衬里法兰盖（BL(S)）无 GB 对应表，仍复用 HG/T 20592')
        else:
            note = ('Class 系列 6 类为真值表（扫描件抽样复核）；'
                    '其余页签仍复用 HG/T 20615 尺寸表')
        return {'status': 'alias', 'label': REVIEW_LABELS['alias'],
                'source': note}
    for prefix, status, note in DATA_REVIEW:
        if csvf.startswith(prefix):
            return {'status': status, 'label': REVIEW_LABELS[status],
                    'source': note}
    return {'status': 'unknown', 'label': REVIEW_LABELS['unknown'],
            'source': '来源未登记'}


def attach_review(rows, review):
    """给导出副本补充“复核状态”，来源为空时补“数据来源”。"""
    out = [dict(r) for r in rows]
    for row in out:
        row.setdefault('复核状态', review.get('label', ''))
        if review.get('source'):
            row.setdefault('数据来源', review['source'])
    return out


def annotate_rows(rows, csvf, std=''):
    """给加载后的每一行附加行级复核状态、来源与面型完整性。

    行内若已有 review_status / review_source（例如未来按行核对的数据表），
    优先使用行值；否则继承文件级 review_for()。返回新列表，不修改原行。
    """
    base = review_for(csvf, std)
    out = []
    is_flange = csvf.startswith(('GBT9124', 'HGT20592', 'HGT20615',
                                 'HGT20623', 'NBT47023'))
    for raw in rows:
        row = dict(raw)
        status = (row.get('review_status') or row.get('复核状态代码')
                  or base.get('status', 'unknown'))
        source = (row.get('review_source') or row.get('数据来源')
                  or base.get('source', ''))
        row['review_status'] = status
        row['review_label'] = REVIEW_LABELS.get(status, status)
        row['复核状态'] = row['review_label']
        row['review_source'] = source
        row['数据来源'] = source
        if is_flange:
            has_face = bool(str(row.get('RF_d', '')).strip()) and \
                bool(str(row.get('RF_f1', '')).strip())
            row['face_status'] = 'complete' if has_face else 'missing'
            row['face_label'] = ('面型尺寸完整' if has_face
                                 else '面型尺寸缺失')
        out.append(row)
    return out


# 标准覆盖矩阵（标准号、名称、收录范围、状态、说明）
STANDARDS_COVERAGE = [
    ('HG/T 20592-2009', '钢制管法兰（PN 系列）', '10 类法兰', 'partial',
     '原程序 CSV，未逐条核对 PDF'),
    ('HG/T 20615-2009', '钢制管法兰（Class 系列）', '8 类法兰', 'partial',
     '原程序 CSV，未逐条核对 PDF'),
    ('HG/T 20623-2009', '大直径钢制管法兰', '4 类法兰', 'partial',
     '原程序 CSV，未逐条核对 PDF'),
    ('NB/T 47023-2012', '长颈对焊法兰（容器法兰）', '1 类法兰', 'partial',
     '原程序 CSV，未逐条核对 PDF'),
    ('GB/T 9124.1-2019', '钢制管法兰 第1部分：PN 系列', '9 类法兰（PDF 复核）',
     'verified', 'WN 表27–38 逐项复核；其余 8 类按表6、表8–91 重建并复核'),
    ('GB/T 9124.1-2019（其余型式）', 'PN 系列 SO/PL/SW/Th/BL/IF/PJSE/PJRJ',
     '表8–91，共 1143 行', 'verified',
     '公共尺寸按 PDF 逐项复核；密封面 d/f1 取表6；质量等非尺寸列沿用 HG/T 参考值'),
    ('GB/T 9124.2-2019', '钢制管法兰 第2部分：Class 系列', '6 类 PDF 转录表',
     'partial', '扫描件目视抽样复核 Class150（30 规格/223 字段一致）；其余页签复用 HG/T 20615'),
    ('GB/T 9124.2-2019（六类）', '钢制管法兰 Class 系列（PDF 转录）',
     '6 类 / Class150–2500', 'partial',
     '表7–45 转录，Class150 代表表抽样复核通过；扫描件未全量 OCR'),
    ('GB/T 9124.1-2019（对焊）', '钢制管法兰 PN 系列（PDF 转录）',
     'PN2.5–400，DN10–600', 'verified',
     '表27–38 共 209 行逐项复核完成，已修正 31 处 N 系列Ⅱ尺寸'),
    ('GB/T 9124.1-2019（衬里法兰盖）', 'BL(S) 不锈钢衬里法兰盖',
     '复用 HG/T 20592', 'alias',
     'GB/T 9124.1 无对应型式表，暂沿用 HG/T 20592 数据'),
    ('GB/T 13402-2019', '大直径钢制管法兰', '未收录', 'missing',
     '尚未建立数据表'),
    ('JB/T 74~86-2015', '钢制管路法兰（13 项）', '未收录', 'missing',
     '机械行业体系，尚未建立数据表'),
    ('NB/T 47020~47027-2012', '压力容器法兰（除 47023）', '未收录', 'missing',
     '其余 7 项尚未建立数据表'),
    ('HG/T 20606-2009', '非金属平垫片（PN 系列）', 'FF/RF/MFM/TG', 'partial',
     '干净 OCR 转写'),
    ('HG/T 20607-2009', 'PTFE 包覆垫片', '1 类', 'inferred',
     '公开标准表补全'),
    ('HG/T 20609-2009', '金属包覆垫片', '1 类', 'partial', '干净 OCR 转写'),
    ('HG/T 20610-2009', '缠绕式垫片（PN 系列）', '1 类', 'inferred',
     '公开标准表补全'),
    ('HG/T 20611-2009', '齿形组合垫（PN 系列）', '1 类', 'inferred',
     '公开标准表补全'),
    ('HG/T 20612-2009', '金属环垫（PN 系列）', '1 类', 'inferred',
     '公开标准表补全'),
    ('HG/T 20627-2009', '非金属平垫片（Class 系列）', '仅 Class 150/300/600',
     'partial', 'PDF 抽样 D1/D2/T 一致；覆盖不全'),
    ('HG/T 20631-2009', '缠绕式垫片（Class 系列）', '1 类', 'inferred',
     '公开标准表补全'),
    ('GB/T 17395-2024', '无缝钢管尺寸与重量', '普通/精密/不锈钢', 'verified',
     '标准 PDF 全文录入'),
    ('ASME B36.10M/B36.19M', '钢管（美标）', 'Sch 系列', 'partial',
     '公开表转写，未核对原版'),
    ('HGJ 514 / 528 / HG/T 20553', '化工配管用钢管', '壁厚系列', 'partial',
     '老标准/来源未归档'),
    ('GB/T 12459/13401-2017', '钢制对焊管件', '弯头/三通/异径管/管帽',
     'partial', '标准表转写'),
    ('70B125-2002', 'U形波纹管膨胀节设计规定', '表A.1', 'partial',
     '原件缺失，数据待复核'),
]

