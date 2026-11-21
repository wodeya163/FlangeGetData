# Reconstructed from bytecode by split_decompile.py
# personal_store.pyc

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
    c = _conn()
    c.execute("CREATE TABLE IF NOT EXISTS torque_records (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            thread_type TEXT NOT NULL,\n            spec TEXT NOT NULL,\n            grade_material TEXT NOT NULL,\n            source TEXT DEFAULT '试验值',\n            t_min REAL, t_rec REAL NOT NULL, t_max REAL,\n            scenario TEXT DEFAULT '',\n            note TEXT DEFAULT '',\n            created_at TEXT DEFAULT (datetime('now','localtime')))")
    c.execute("CREATE TABLE IF NOT EXISTS custom_materials (\n            id INTEGER PRIMARY KEY AUTOINCREMENT,\n            name TEXT UNIQUE NOT NULL,\n            sigma_y REAL NOT NULL,\n            sigma_b REAL,\n            note TEXT DEFAULT '',\n            created_at TEXT DEFAULT (datetime('now','localtime')))")
    None(None, None)
    return None
    with None:
        if not None:
            pass
def _row_dict(r):
    return r.keys()() if not r is None else None
def add_record(thread_type, spec, grade_material, source, t_rec, t_min, t_max, scenario, note):
    '''新增记录。t_min/t_max 缺省按底账风格 0.85/1.15 自动补齐。返回新 id。'''
    t_rec = float(t_rec)
    if not t_min is not None:
        t_min = round(t_rec * MIN_RATIO, 1)
    if not t_max is not None:
        t_max = round(t_rec * MAX_RATIO, 1)
    c = _conn()
    cur = c.execute('INSERT INTO torque_records (thread_type,spec,grade_material,source,t_min,t_rec,t_max,scenario,note) VALUES (?,?,?,?,?,?,?,?,?)', (thread_type, spec, grade_material, source, float(t_min), t_rec, float(t_max), scenario, note))
    (None, None)
    return None, cur.lastrowid
    with None:
        if not None:
            pass
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
    vals = []
    sets = []
    for k, v in fields.items():
        if k in allowed:
            sets.append(f'''{k}=?''')
            vals.append(v)
        if not sets:
            return False
        None.append(rec_id)
        c = _conn()
        c.execute(f'''UPDATE torque_records SET {', '.join(sets)} WHERE id=?''', vals)
        None(None, None)
    with None:
        if not None:
            pass
    return True
def delete_record(rec_id):
    c = _conn()
    c.execute('DELETE FROM torque_records WHERE id=?', (rec_id,))
    (None, None)
    return None, c.total_changes > 0
    with None:
        if not None:
            pass
def get_record(rec_id):
    c = _conn()
    r = c.execute('SELECT * FROM torque_records WHERE id=?', (rec_id,)).fetchone()
    (None, None)
    return None, _row_dict(r)
    with None:
        if not None:
            pass
def list_records(search, thread_type, source):
    '''按关键字(规格/等级材质/备注)与筛选条件列记录, 推荐值升序。'''
    sql = 'SELECT * FROM torque_records WHERE 1=1'
    vals = []
    if search:
        sql += ' AND (spec LIKE ? OR grade_material LIKE ? OR note LIKE ?)'
        vals += [
            f'''%{search}%'''] * 3
    if thread_type:
        sql += ' AND thread_type=?'
        vals.append(thread_type)
    if source:
        sql += ' AND source=?'
        vals.append(source)
    sql += ' ORDER BY spec, grade_material, t_rec'
    c = _conn()
    (None, None)
    return (lambda .0: [ _row_dict(r) for r in .0 ]), c.execute(sql, vals)()
    with None:
        if not None:
            pass
def match_records(thread_type, spec, grade_material, limit):
    '''按 螺纹类型+规格(+等级材质) 匹配个人记录, 推荐值升序, 最多 limit 条。'''
    sql = 'SELECT * FROM torque_records WHERE thread_type=? AND spec=?'
    vals = [
        thread_type,
        spec]
    if grade_material:
        sql += ' AND grade_material=?'
        vals.append(grade_material)
    sql += ' ORDER BY t_rec LIMIT ?'
    vals.append(limit)
    c = _conn()
    (None, None)
    return (lambda .0: [ _row_dict(r) for r in .0 ]), c.execute(sql, vals)()
    with None:
        if not None:
            pass
def count_records():
    c = _conn()
    (None, None)
    return None, c.execute('SELECT COUNT(*) FROM torque_records').fetchone()[0]
    with None:
        if not None:
            pass
def add_material(name, sigma_y, sigma_b, note):
    name = name.strip()
    if not name:
        raise ValueError('材料名不能为空')
    if not  <= 50, float(sigma_y) or 50, float(sigma_y) <= 3000:
        pass

    raise ValueError('屈服强度应在 50~3000 MPa 之间')
    c.execute('INSERT INTO custom_materials (name,sigma_y,sigma_b,note) VALUES (?,?,?,?)', (name, float(sigma_y), float(sigma_b) if sigma_b else None, note))
    _conn()(None, None)
    return None
    with None:
        if not None:
            pass
def update_material(mat_id, **fields):
    allowed = {
        'name',
        'note',
        'sigma_b',
        'sigma_y'}
    vals = []
    sets = []
    for k, v in fields.items():
        if k in allowed:
            sets.append(f'''{k}=?''')
            vals.append(v)
        if not sets:
            return False
        None.append(mat_id)
        c = _conn()
        c.execute(f'''UPDATE custom_materials SET {', '.join(sets)} WHERE id=?''', vals)
        None(None, None)
    with None:
        if not None:
            pass
    return True
def delete_material(mat_id):
    c = _conn()
    c.execute('DELETE FROM custom_materials WHERE id=?', (mat_id,))
    (None, None)
    return None, c.total_changes > 0
    with None:
        if not None:
            pass
def list_materials():
    c = _conn()
    (None, None)
    return (lambda .0: [ _row_dict(r) for r in .0 ]), c.execute('SELECT * FROM custom_materials ORDER BY name')()
    with None:
        if not None:
            pass
def get_material(name):
    '''按名称取材料, 返回 dict 或 None（供计算线程直接调用）。'''
    c = _conn()
    r = c.execute('SELECT * FROM custom_materials WHERE name=?', (name,)).fetchone()
    (None, None)
    return None, _row_dict(r)
    with None:
        if not None:
            pass
def backup_db(reason):
    '''备份 personal.db, 保留最近 3 份。返回备份路径。'''
    if not os.path.exists(DB_PATH):
        return None
    stamp = None.datetime.now().strftime('%Y%m%d_%H%M%S')
    bak = os.path.join(_APP_DIR, f'''personal.db.bak_{reason}_{stamp}''')
    shutil.copy2(DB_PATH, bak)
    import glob
    olds = sorted(glob.glob(os.path.join(_APP_DIR, 'personal.db.bak_*')), key = os.path.getmtime)
    for old in olds[:-3]:
        os.remove(old)
        except OSError:
            continue
        return bak
def validate_record_row(row):
    '''校验一行导入数据, 返回 (规整后 dict, 错误信息)。错误时 dict 为 None。'''

    try:
        tt = str(row.get('螺纹类型', '')).strip()
        if tt not in THREAD_TYPES:
            return (None, f'''螺纹类型 \'{tt}\' 须为 {'/'.join(THREAD_TYPES)}''')
        spec = None(row.get('规格', '')).strip().upper().replace('Ｍ', 'M').replace('×', '×')
        if tt == '自攻':
            if not re.match('^ST\\d+(\\.\\d+)?$', spec):
                return (None, f'''自攻规格 \'{spec}\' 须形如 ST4.2''')
        if not re.match('^M\\d+(×[\\d.]+)?$', spec):
            return (None, f'''规格 \'{spec}\' 须形如 M12 或 M12×1.5''')
        if None == '细牙' and '×' not in spec:
            return (None, f'''细牙规格 \'{spec}\' 须带螺距, 如 M12×1.5''')
        gm = None(row.get('等级或材质', '')).strip()
        if not gm:
            return (None, '等级或材质不能为空')
        if not None(row.get('来源', '试验值')).strip():
            src = '试验值'
            if src not in SOURCES:
                return (None, f'''来源 \'{src}\' 须为 {'/'.join(SOURCES)}''')

            def _num(key):
                v = row.get(key)
                if v in (None, '', '—', '-'):
                    return None
                return None(str(v).replace(',', ''))
            t_rec = _num('推荐力矩(N·m)')
            if t_rec is None or t_rec <= 0:
                return (None, '推荐力矩须为正数')
            t_min = _num('最小力矩(N·m)')
            t_max = _num('最大力矩(N·m)')
            if t_min is None and t_min >= t_rec:
                return (None, '最小力矩应小于推荐力矩')
            if None is None and t_max <= t_rec:
                return (None, '最大力矩应大于推荐力矩')
            if not row.get('场景', ''):
                scen = None('').strip()
                if not row.get('备注', ''):
                    note = str('').strip()
                    return (dict(thread_type = tt, spec = spec, grade_material = gm, source = src, t_min = t_min, t_rec = t_rec, t_max = t_max, scenario = scen, note = note), '')
                except (TypeError, ValueError):
                    e = str
                    del e
                    return None
                    None = 
                    del e
def import_records(rows, mode):
    '''批量导入。mode: append=追加 / rebuild=清空后重灌(先备份)。
    返回 (成功数, [(行号, 错误)])。'''
    if mode == 'rebuild':
        backup_db('rebuild')
    errs = []
    ok = 0
    if mode == 'rebuild':
        c = _conn()
        c.execute('DELETE FROM torque_records')
        None(None, None)
    else:
        with None:
            if not None:
                pass
# WARNING: Decompyle incomplete
def smart_baseline(thread_type, spec, grade_material):
    pass


def stats_summary():
    pass


try:
    init_db()
    return None
except Exception:
    return None
