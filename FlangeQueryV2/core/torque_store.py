# Source Generated with Decompyle++
# Decompiled by MUHAMMAD SHAKIB
# GitHub: https://github.com/0xSHAK1B
# File: personal_store.pyc (Python 3.11)

'''
个人库数据层（V2.2）
- torque_records: 用户自录扭矩记录（试验值/工艺卡/厂商样本等）
- custom_materials: 自定义材料参数（σy/σb），供 T=K·F·d 实时计算
存储: ~/.TorqueTool/personal.db（用户数据, 不打进 EXE）
导入/覆盖前自动备份最近 3 份。
'''
import os
import sqlite3
import shutil
import datetime
import re
_APP_DIR = os.path.join(os.path.expanduser('~'), '.TorqueTool')
os.makedirs(_APP_DIR, exist_ok = True)
DB_PATH = os.path.join(_APP_DIR, 'personal.db')
THREAD_TYPES = ('粗牙', '细牙', '自攻')
SOURCES = ('试验值', '工艺卡', '厂商样本', '经验', '其他')
(MIN_RATIO, MAX_RATIO) = (0.85, 1.15)
_COLS = ('id', 'thread_type', 'spec', 'grade_material', 'source', 't_min', 't_rec', 't_max', 'scenario', 'note', 'created_at')
def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS torque_records (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            thread_type TEXT NOT NULL,\n            spec TEXT NOT NULL,\n            grade_material TEXT NOT NULL,\n            source TEXT DEFAULT '试验值',\n            t_min REAL, t_rec REAL NOT NULL, t_max REAL,\n            scenario TEXT DEFAULT '',\n            note TEXT DEFAULT '',\n            created_at TEXT DEFAULT (datetime('now','localtime')))")
        c.execute("CREATE TABLE IF NOT EXISTS custom_materials (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            name TEXT UNIQUE NOT NULL,\n            sigma_y REAL NOT NULL,\n            sigma_b REAL,\n            note TEXT DEFAULT '',\n            created_at TEXT DEFAULT (datetime('now','localtime')))")

def _row_dict(r):
    return {k: r[k] for k in r.keys()} if r is not None else None


def add_record(thread_type, spec, grade_material, source, t_rec, t_min = None, t_max = None, scenario = '', note = ''):
    '''新增记录。t_min/t_max 缺省按底账风格 0.85/1.15 自动补齐。返回新 id。'''
    t_rec = float(t_rec)
    if t_min is None:
        t_min = round(t_rec * MIN_RATIO, 1)
    if t_max is None:
        t_max = round(t_rec * MAX_RATIO, 1)
    with _conn() as c:
        cur = c.execute('INSERT INTO torque_records (thread_type,spec,grade_material,source,t_min,t_rec,t_max,scenario,note) VALUES (?,?,?,?,?,?,?,?,?)', (thread_type, spec, grade_material, source, float(t_min), t_rec, float(t_max), scenario, note))
        return cur.lastrowid


def update_record(rec_id, **fields):
    '''按 id 更新任意字段（白名单校验）。'''
    allowed = {
        'note',
        'spec',
        't_max',
        't_min',
        't_rec',
        'source',
        'scenario',
        'thread_type',
        'grade_material'}
    (sets, vals) = ([], [])
    for k, v in fields.items():
        if k in allowed:
            sets.append(f'{k}=?')
            vals.append(v)
    if not sets:
        return False
    vals.append(rec_id)
    with _conn() as c:
        c.execute(f'''UPDATE torque_records SET {', '.join(sets)} WHERE id=?''', vals)
    return True


def delete_record(rec_id):
    with _conn() as c:
        c.execute('DELETE FROM torque_records WHERE id=?', (rec_id,))
        return c.total_changes > 0


def get_record(rec_id):
    with _conn() as c:
        r = c.execute('SELECT * FROM torque_records WHERE id=?', (rec_id,)).fetchone()
        return _row_dict(r)


def list_records(search = '', thread_type = '', source = ''):
    '''按关键字(规格/等级材质/备注)与筛选条件列记录, 推荐值升序。'''
    sql = 'SELECT * FROM torque_records WHERE 1=1'
    vals = []
    if search:
        sql += ' AND (spec LIKE ? OR grade_material LIKE ? OR note LIKE ?)'
        vals += [f'%{search}%'] * 3
    if thread_type:
        sql += ' AND thread_type=?'
        vals.append(thread_type)
    if source:
        sql += ' AND source=?'
        vals.append(source)
    sql += ' ORDER BY spec, grade_material, t_rec'
    with _conn() as c:
        return [_row_dict(r) for r in c.execute(sql, vals)]


def match_records(thread_type, spec, grade_material = None, limit = 4):
    '''按 螺纹类型+规格(+等级材质) 匹配个人记录, 推荐值升序, 最多 limit 条。'''
    sql = 'SELECT * FROM torque_records WHERE thread_type=? AND spec=?'
    vals = [thread_type, spec]
    if grade_material:
        sql += ' AND grade_material=?'
        vals.append(grade_material)
    sql += ' ORDER BY t_rec LIMIT ?'
    vals.append(limit)
    with _conn() as c:
        return [_row_dict(r) for r in c.execute(sql, vals)]


def count_records():
    with _conn() as c:
        return c.execute('SELECT COUNT(*) FROM torque_records').fetchone()[0]


def add_material(name, sigma_y, sigma_b = None, note = ''):
    name = name.strip()
    if not name:
        raise ValueError('材料名不能为空')
    if not 50 <= float(sigma_y) <= 3000:
        raise ValueError('屈服强度应在 50~3000 MPa 之间')
    with _conn() as c:
        c.execute('INSERT INTO custom_materials (name,sigma_y,sigma_b,note) VALUES (?,?,?,?)', (name, float(sigma_y), float(sigma_b) if sigma_b else None, note))


def update_material(mat_id, **fields):
    allowed = {
        'name',
        'note',
        'sigma_b',
        'sigma_y'}
    (sets, vals) = ([], [])
    for k, v in fields.items():
        if k in allowed:
            sets.append(f'{k}=?')
            vals.append(v)
    if not sets:
        return False
    vals.append(mat_id)
    with _conn() as c:
        c.execute(f'''UPDATE custom_materials SET {', '.join(sets)} WHERE id=?''', vals)
    return True


def delete_material(mat_id):
    with _conn() as c:
        c.execute('DELETE FROM custom_materials WHERE id=?', (mat_id,))
        return c.total_changes > 0


def list_materials():
    with _conn() as c:
        return [_row_dict(r) for r in c.execute('SELECT * FROM custom_materials ORDER BY name')]


def get_material(name):
    '''按名称取材料, 返回 dict 或 None（供计算线程直接调用）。'''
    with _conn() as c:
        r = c.execute('SELECT * FROM custom_materials WHERE name=?', (name,)).fetchone()
        return _row_dict(r)


def backup_db(reason = 'manual'):
    '''备份 personal.db, 保留最近 3 份。返回备份路径。'''
    if not os.path.exists(DB_PATH):
        return None
    stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    bak = os.path.join(_APP_DIR, f'personal.db.bak_{reason}_{stamp}')
    shutil.copy2(DB_PATH, bak)
    import glob
    olds = sorted(glob.glob(os.path.join(_APP_DIR, 'personal.db.bak_*')), key = os.path.getmtime)
    for old in olds[:-3]:
        try:
            os.remove(old)
        except OSError:
            continue
    return bak


def validate_record_row(row):
    '''校验一行导入数据, 返回 (规整后 dict, 错误信息)。错误时 dict 为 None。'''
    try:
        tt = str(row.get('螺纹类型', '')).strip()
        if tt not in THREAD_TYPES:
            return (None, f'''螺纹类型 '{tt}' 须为 {'/'.join(THREAD_TYPES)}''')
        spec = str(row.get('规格', '')).strip().upper().replace('Ｍ', 'M').replace('×', '×')
        if tt == '自攻':
            if not re.match('^ST\\d+(\\.\\d+)?$', spec):
                return (None, f'''自攻规格 '{spec}' 须形如 ST4.2''')
        elif not re.match('^M\\d+(×[\\d.]+)?$', spec):
            return (None, f'''规格 '{spec}' 须形如 M12 或 M12×1.5''')
        if tt == '细牙' and '×' not in spec:
            return (None, f'''细牙规格 '{spec}' 须带螺距, 如 M12×1.5''')
        gm = str(row.get('等级或材质', '')).strip()
        if not gm:
            return (None, '等级或材质不能为空')
        src = str(row.get('来源', '试验值')).strip() or '试验值'
        if src not in SOURCES:
            return (None, f'''来源 '{src}' 须为 {'/'.join(SOURCES)}''')

        def _num(key):
            v = row.get(key)
            if v in (None, '', '—', '-'):
                return None
            return float(str(v).replace(',', ''))

        t_rec = _num('推荐力矩(N·m)')
        if t_rec is None or t_rec <= 0:
            return (None, '推荐力矩须为正数')
        t_min = _num('最小力矩(N·m)')
        t_max = _num('最大力矩(N·m)')
        if t_min is not None and t_min >= t_rec:
            return (None, '最小力矩应小于推荐力矩')
        if t_max is not None and t_max <= t_rec:
            return (None, '最大力矩应大于推荐力矩')
        scen = str(row.get('场景', '') or '').strip()
        note = str(row.get('备注', '') or '').strip()
        return (dict(thread_type = tt, spec = spec, grade_material = gm, source = src, t_min = t_min, t_rec = t_rec, t_max = t_max, scenario = scen, note = note), '')
    except (TypeError, ValueError) as e:
        return (None, f'数值格式错误: {e}')


def import_records(rows, mode = 'append'):
    '''批量导入。mode: append=追加 / rebuild=清空后重灌(先备份)。
    返回 (成功数, [(行号, 错误)])。'''
    if mode == 'rebuild':
        backup_db('rebuild')
    (ok, errs) = (0, [])
    if mode == 'rebuild':
        with _conn() as c:
            c.execute('DELETE FROM torque_records')
    for i, raw in enumerate(rows, start = 2):
        (rec, err) = validate_record_row(raw)
        if err:
            errs.append((i, err))
            continue
        try:
            add_record(**rec)
            ok += 1
        except Exception as e:
            errs.append((i, str(e)))
    return (ok, errs)


def smart_baseline(thread_type, spec, grade_material):
    '''为一条个人记录推算「智能底账」参考值 (只读, 不修改任何数据)。
    返回 (rec N·m 或 None, 说明文字)。
    规则:
      粗牙/细牙 — 标准等级查底账表(细牙按 As 比修正); ★自定义材料按 T=K·F·d 用 σy 计算
      自攻     — 按被材精确匹配, 写法不全时模糊匹配(多匹配取最高值并注明)
      其他     — (None, 原因), UI 显示 '—'
    '''
    from core import torque_data as TD
    gm = (grade_material or '').lstrip('★').strip()
    tt = (thread_type or '').strip()
    if tt in ('粗牙', '细牙'):
        mat = None
        if gm:
            mat = get_material(gm)
        if mat:
            (_, rec, _) = TD.calc_torque_from_sigma(mat['sigma_y'], spec or '')
            if rec:
                return (rec, f'''★{gm} σy={mat['sigma_y']:.0f}MPa''')
            return (None, '材料有σy但规格无法计算')
        if gm in TD.YIELD_STRENGTH:
            if tt == '细牙':
                (_, rec, _) = TD.calc_fine_thread_torque(gm, spec or '', 'hex')
            else:
                t = TD.get_torque('hex', spec or '', gm)
                rec = t[1] if t and t[1] is not None else None
            if rec:
                return (rec, f'{gm} 级')
            return (None, '底账无此规格×等级')
        return (None, '非标准等级且未录同σy材料')
    if tt == '自攻':
        data = TD.SELF_TAPPING.get(spec or '', {})
        if not data:
            return (None, '底账无此自攻规格')
        if gm in data:
            return (data[gm][1], gm)
        hits = [(k, v[1]) for k, v in data.items() if gm and (gm in k or k in gm)]
        if len(hits) == 1:
            return (hits[0][1], hits[0][0])
        if len(hits) > 1:
            (k, rec) = max(hits, key = lambda x: x[1])
            return (rec, f'{k} (模糊匹配取最高)')
        return (None, '被材写法对不上, 改成如「薄钢板/铝板/塑料」')
    return (None, '未知螺纹类型')


def stats_summary():
    '''个人库统计: 记录总数 / 覆盖规格数 / 自定义材料数 / 最近录入日期。'''
    with _conn() as c:
        n_rec = c.execute('SELECT COUNT(*) FROM torque_records').fetchone()[0]
        n_spec = c.execute("SELECT COUNT(DISTINCT thread_type || '|' || spec) FROM torque_records").fetchone()[0]
        latest = c.execute('SELECT MAX(created_at) FROM torque_records').fetchone()[0]
    return dict(n_records = n_rec, n_specs = n_spec, n_materials = len(list_materials()), latest = (latest or '')[:10])


try:
    init_db()
except Exception:
    pass
