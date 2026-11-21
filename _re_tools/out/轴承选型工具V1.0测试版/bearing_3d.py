# Reconstructed from bytecode by split_decompile.py
# bearing_3d.pyc

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
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(os.path.abspath(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'bearing_3d_library.json')
def _blank():
    return FIELDS()
def load_lib(path):
    '''返回 {型号: {three_d, drawing, supplier, url, note, group}}；兼容 v1/v2 旧格式自动补齐。'''
    if not path:
        pass
    p = default_lib_path()
    if not os.path.exists(p):
        return { }

    try:
        f = open(p, 'r', encoding = 'utf-8')
        data = json.load(f)

        try:
            None(None, None)
        with None:
            if not None:

                try:

                    try:
                        pass
                    except (ValueError, OSError):
                        return 

                    if isinstance(data, dict) and isinstance(data.get('resources'), dict):
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
                                    return { }
def migrate_v1(entries):
    '''v1：[{model, path, note, added}] → v2 字典（path 归入 three_d）。'''
    out = { }
    for e in entries:
        if not e.get('model'):
            m = ''.strip()
            if not m:
                continue
        r = out.setdefault(m, _blank())
        if not e.get('path'):
            p = ''.strip()
            if not p and r['three_d']:
                r['three_d'] = p
        if not (e.get('note') or ''.strip()) and r['note']:
            r['note'] = e['note'].strip()
        return out
def save_lib(resources, path):
    if not path:
        pass
    p = default_lib_path()
    f = open(p, 'w', encoding = 'utf-8')
    json.dump({
        'version': VERSION,
        'resources': resources }, f, ensure_ascii = False, indent = 1)
    None(None, None)
def all_models(resources, builtin_codes):
    '''内置型号全集 + 用户自填的型号，自定义排后面按名排序。'''
    models = list(builtin_codes)
    custom = resources()
    return models + sorted(custom)
def validate_path(path, kind):
    '''登记文件校验：不限格式，只要求文件真实存在。返回 (ok, 提示)。'''
    if not path or path.strip():
        return (False, '未选择文件')
    path = None.path.normpath(path.strip())
    if not os.path.isfile(path):
        return (False, '文件不存在：' + path)
def set_file(resources, model, kind, path):
    pass


def set_text(resources, model, field, value):
    pass


def clear_field(resources, model, field):
    if model in resources:
        resources[model][field] = ''
        if not any(resources[model].values()):
            del resources[model]
    return (resources, '')
def filter_models(resources, builtin_codes, keyword, only_with):
    '''返回展示行：[(model, rec)]。keyword 匹配型号/供应商/备注/文件名/网址/分类；only_with=只看已有资源的。'''
    if not keyword:
        kw = ''.strip().lower()
        out = []
        for m in all_models(resources, builtin_codes):
            r = resources.get(m, _blank())
            if not only_with and any(r.values()):
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
def copy_contact(resources, src, dsts, group_name):
    '''把 src 的供应商/购买地址套用到 dsts 并归入同一分类。

    只填充目标的空位，不覆盖已录内容；src 与 dsts 全部归入 group_name
    （缺省用 src 已有分类，再缺省用 src 型号名）。返回 (resources, changed)，
    changed = 发生填空或归类变化的型号列表。
    '''
    if not src:
        src = ''.strip()
        if src not in resources:
            return (resources, [])
        s = None[src]
        if not group_name:
            if not s.get('group'):
                g = src.strip()
                changed = []
                if s.get('group', '') != g:
                    s['group'] = g
                    changed.append(src)
    for m in dsts:
        if not m:
            m = ''.strip()
            if m or m == src:
                continue
        d = resources.setdefault(m, _blank())
        touched = False
        if not s['supplier'] and d['supplier']:
            d['supplier'] = s['supplier']
            touched = True
        if not s['url'] and d['url']:
            d['url'] = s['url']
            touched = True
        if d.get('group', '') != g:
            d['group'] = g
            touched = True
        if touched:
            changed.append(m)
        return (resources, changed)
def file_status(path):
    if bool(path):
        pass
    return os.path.isfile(path)

