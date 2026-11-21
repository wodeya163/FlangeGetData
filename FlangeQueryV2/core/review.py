# -*- coding: utf-8 -*-
"""数据来源、复核状态与标准覆盖矩阵（无 Qt 依赖）。"""

# GB/T 9124 页签目前复用 HG/T 尺寸表，必须在界面、打印与导出中显式标注来源
PROVENANCE = {
    'GB/T 9124.1-2019（PN 系列·欧洲体系）':
        '数据源：HG/T 20592-2009（GB/T 9124.1 PDF 抽样 30 行发现 6 处差异，待逐条复核）',
    'GB/T 9124.2-2019（Class 系列·美洲体系）':
        '数据源：HG/T 20615-2009（GB/T 9124.2 PDF 为扫描件，待 OCR 复核）',
}


def source_note(std, csvf=''):
    if csvf.startswith('GBT9124_1_'):
        return '数据源：GB/T 9124.1-2019 表27–38（PN2.5–400，DN≤600）'
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
    if csvf.startswith('GBT9124_1_'):
        return {'status': 'partial', 'label': REVIEW_LABELS['partial'],
                'source': 'GB/T 9124.1-2019 表27–38 转录（PN2.5–400，DN≤600）'}
    if csvf.startswith('GBT9124_2_带颈对焊'):
        return {'status': 'partial', 'label': REVIEW_LABELS['partial'],
                'source': 'GB/T 9124.2-2019 表19–24 转录（Class150–2500）'}
    if csvf.startswith('GBT9124_2_带颈平焊'):
        return {'status': 'partial', 'label': REVIEW_LABELS['partial'],
                'source': 'GB/T 9124.2-2019 表25–29 转录（SO Class150–1500）'}
    if csvf.startswith('GBT9124_2_整体'):
        return {'status': 'partial', 'label': REVIEW_LABELS['partial'],
                'source': 'GB/T 9124.2-2019 表7–12 转录（IF Class150–2500）'}
    if csvf.startswith('GBT9124_2_承插焊'):
        return {'status': 'partial', 'label': REVIEW_LABELS['partial'],
                'source': 'GB/T 9124.2-2019 表30–33 转录（SW Class150–1500）'}
    if csvf.startswith('GBT9124_2_螺纹'):
        return {'status': 'partial', 'label': REVIEW_LABELS['partial'],
                'source': 'GB/T 9124.2-2019 表13–18 转录（Th Class150–2500）'}
    if csvf.startswith('GBT9124_2_法兰盖'):
        return {'status': 'partial', 'label': REVIEW_LABELS['partial'],
                'source': 'GB/T 9124.2-2019 表40–45 转录（BL Class150–2500）'}
    if std.startswith('GB/T 9124'):
        if '9124.1' in std:
            note = ('复用 HG/T 20592 尺寸表；GB/T 9124.1 PDF 抽样 30 行'
                    '发现 6 处差异（S_min/r/H）')
        else:
            note = '复用 HG/T 20615 尺寸表；GB/T 9124.2 PDF 为扫描件，待 OCR 复核'
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
    ('GB/T 9124.1-2019', '钢制管法兰 第1部分：PN 系列', '复用 HG/T 20592',
     'alias', 'GB/T 真值待逐条转录'),
    ('GB/T 9124.2-2019', '钢制管法兰 第2部分：Class 系列', '复用 HG/T 20615',
     'alias', 'GB/T 真值待逐条转录'),
    ('GB/T 9124.2-2019（对焊）', '钢制管法兰 Class 系列（PDF 转录）',
     'Class150–2500', 'partial', '表19–24 转录；其余型式仍复用 HG/T'),
    ('GB/T 9124.1-2019（对焊）', '钢制管法兰 PN 系列（PDF 转录）',
     'PN2.5–400，DN10–600', 'partial', '表27–38 转录；其余型式仍复用 HG/T'),
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

