# -*- coding: utf-8 -*-
"""CSV 读取、列名归一与数值工具（无 Qt 依赖）。"""

import csv
import logging
import os

logger = logging.getLogger('flangequery')

COLUMN_ALIASES = {
    'kg': 'm_kg',
    'RJ_R': 'RJ_r',
    'PN2': 'Class',
}


def _normalize_columns(head, rows):
    """统一历史列名，去掉重复列与 Class 体系的伪 PN 列。

    - kg → m_kg；RJ_R → RJ_r；PN2 → Class；
    - 去掉 pandas 去重后缀列（如 RF_d.1）；
    - Class 体系的 PN 列若为 class_150 之类的伪值，整列移除。
    """
    renamed = []
    mapping = {}
    for name in head:
        target = COLUMN_ALIASES.get(name, name)
        if target in renamed:
            mapping[name] = target
            continue
        renamed.append(target)
        if target != name:
            mapping[name] = target
    if mapping:
        rows = [{mapping.get(k, k): v for k, v in r.items()} for r in rows]
    head = renamed
    for name in list(head):
        if name.endswith('.1') and name[:-2] in head:
            head.remove(name)
            for r in rows:
                r.pop(name, None)
    if 'Class' in head and 'PN' in head:
        values = [str(r.get('PN', '')).strip() for r in rows]
        if all(v == '' or v.lower().startswith('class') for v in values):
            head.remove('PN')
            for r in rows:
                r.pop('PN', None)
    if ('Class' in head and 'DN' in head and 'DN2' in head
            and any(str(r.get('Class', '')).strip() for r in rows)
            and any('"' in str(r.get('DN', '')) for r in rows)):
        # Class 体系原表 DN 为英寸、DN2 为毫米，与其它表相反；统一为 DN=mm
        head = [('DN2' if h == 'DN' else 'DN' if h == 'DN2' else h)
                for h in head]
        rows = [{('DN2' if k == 'DN' else 'DN' if k == 'DN2' else k): v
                 for k, v in r.items()} for r in rows]
    return head, rows


def load_csv(path):
    """读 CSV → (列名列表, 行列表[dict])。兼容 utf-8/gbk。

    首列为空表头的 CSV（如 HG/T 20592 各表）首列是行号，需要连同数据行一起
    裁掉；表头与数据行必须用同一份裁剪后的行集合，不能再对数据二次切片，
    否则会丢掉第一条记录（PN10/DN10 丢失的历史 bug）。
    """
    for enc in ('utf-8-sig', 'gbk', 'latin1'):
        try:
            with open(path, encoding=enc, newline='') as f:
                raw = list(csv.reader(f))
            break
        except UnicodeDecodeError:
            continue
    else:
        raise IOError('无法解码: ' + path)
    head = [h.strip() for h in raw[0]]
    data_rows = raw[1:]
    if head and head[0] == '':
        head = head[1:]
        data_rows = [r[1:] for r in data_rows]
    data = []
    skipped = []
    for lineno, r in enumerate(data_rows, start=2):
        if not r:
            continue
        if len(r) != len(head):
            skipped.append(lineno)
            continue
        data.append(dict(zip(head, r)))
    if skipped:
        logger.warning('%s 有 %d 行列数不符已跳过：%s',
                       os.path.basename(path), len(skipped), skipped[:20])
    return _normalize_columns(head, data)


