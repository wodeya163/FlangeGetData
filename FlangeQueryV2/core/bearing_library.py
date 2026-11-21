# Source Generated with Decompyle++
# Decompiled by MUHAMMAD SHAKIB
# GitHub: https://github.com/0xSHAK1B
# File: bearing_3d.pyc (Python 3.11)

'''资源收藏数据层：按型号登记 三维/图纸/供应商/购买地址/备注。

只记录用户自备资源的本地地址，绝不内嵌文件本体。
存储：与程序同目录 bearing_3d_library.json（打包后随 EXE 目录，绿色便携）。
格式 v3：{"version":3, "resources": {型号: {three_d, drawing, supplier, url, note, group}}}
v2 同构少 group 字段、v1（entries 列表）读入后自动迁移；group 用于「套用供应商/地址后归为一类」。
'''
import json
import os
import sys
VERSION = 3
FIELDS = ('three_d', 'drawing', 'supplier', 'url', 'note', 'group')
THREE_D_EXT = {
    '.igs',
    '.obj',
    '.prt',
    '.sat',
    '.stl',
    '.stp',
    '.x_b',
    '.x_t',
    '.brep',
    '.iges',
    '.step',
    '.sldprt'}
DRAWING_EXT = {
    '.bmp',
    '.dwg',
    '.dxf',
    '.jpg',
    '.pdf',
    '.png',
    '.jpeg',
    '.webp'}
KINDS = {
    'three_d': ('三维', THREE_D_EXT),
    'drawing': ('图纸', DRAWING_EXT) }

def default_lib_path():
    base = os.path.join(os.path.expanduser('~'), '.FlangeQuery')
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, 'bearing_3d_library.json')


def _blank():
    return {f: '' for f in FIELDS}


def load_lib(path=None):
    '''返回 {型号: {three_d, drawing, supplier, url, note, group}}；兼容 v1/v2 旧格式自动补齐。'''
    p = path or default_lib_path()
    if not os.path.exists(p):
        return {}
    try:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (ValueError, OSError):
        return {}
    if isinstance(data, dict) and isinstance(data.get('resources'), dict):
        out = {}
        for model, fields in data['resources'].items():
            e = _blank()
            if isinstance(fields, dict):
                for k, v in fields.items():
                    if k in e and isinstance(v, str):
                        e[k] = v
            out[model] = e
        return out
    if isinstance(data, dict) and isinstance(data.get('entries'), list):
        return migrate_v1(data['entries'])
    return {}


def migrate_v1(entries):
    '''v1：[{model, path, note, added}] → v2 字典（path 归入 three_d）。'''
    out = {}
    for e in entries:
        m = (e.get('model') or '').strip()
        if not m:
            continue
        r = out.setdefault(m, _blank())
        p = (e.get('path') or '').strip()
        if p and not r['three_d']:
            r['three_d'] = p
        if (e.get('note') or '').strip() and not r['note']:
            r['note'] = e['note'].strip()
    return out


def save_lib(resources, path=None):
    p = path or default_lib_path()
    with open(p, 'w', encoding='utf-8') as f:
        json.dump({
            'version': VERSION,
            'resources': resources}, f, ensure_ascii=False, indent=1)
    return p


def all_models(resources, builtin_codes):
    '''内置型号全集 + 用户自填的型号，自定义排后面按名排序。'''
    models = list(builtin_codes)
    custom = [m for m in resources if m not in set(models)]
    return models + sorted(custom)


def validate_path(path, kind=None):
    '''登记文件校验：不限格式，只要求文件真实存在。返回 (ok, 提示)。'''
    if not path or not path.strip():
        return (False, '未选择文件')
    path = os.path.normpath(path.strip())
    if not os.path.isfile(path):
        return (False, '文件不存在：' + path)
    return (True, '')


def set_file(resources, model, kind, path):
    model = (model or '').strip()
    if not model:
        return (resources, '型号为空')
    ok, msg = validate_path(path, kind)
    if not ok:
        return (resources, msg)
    r = resources.setdefault(model, _blank())
    r[kind] = os.path.normpath(path.strip())
    return (resources, '')


def set_text(resources, model, field, value):
    if field not in FIELDS:
        return (resources, '未知字段')
    model = (model or '').strip()
    if not model:
        return (resources, '型号为空')
    r = resources.setdefault(model, _blank())
    r[field] = (value or '').strip()
    return (resources, '')


def clear_field(resources, model, field):
    if model in resources:
        resources[model][field] = ''
        if not any(resources[model].values()):
            del resources[model]
    return (resources, '')


def filter_models(resources, builtin_codes, keyword='', only_with=False):
    kw = (keyword or '').strip().lower()
    out = []
    for m in all_models(resources, builtin_codes):
        r = resources.get(m, _blank())
        if only_with and not any(r.values()):
            continue
        if kw:
            hay = ' '.join([
                m,
                r['supplier'],
                r['note'],
                r['group'],
                os.path.basename(r['three_d']),
                os.path.basename(r['drawing']),
                r['url']]).lower()
            if kw not in hay:
                continue
        out.append((m, r))
    return out


def copy_contact(resources, src, dsts, group_name=None):
    src = (src or '').strip()
    if src not in resources:
        return (resources, [])
    s = resources[src]
    g = (group_name or s.get('group') or src).strip()
    changed = []
    if s.get('group', '') != g:
        s['group'] = g
        changed.append(src)
    for m in dsts:
        m = (m or '').strip()
        if not m or m == src:
            continue
        d = resources.setdefault(m, _blank())
        touched = False
        if s['supplier'] and not d['supplier']:
            d['supplier'] = s['supplier']
            touched = True
        if s['url'] and not d['url']:
            d['url'] = s['url']
            touched = True
        if d.get('group', '') != g:
            d['group'] = g
            touched = True
        if touched:
            changed.append(m)
    return (resources, changed)


def file_status(path):
    return bool(path) and os.path.isfile(path)
