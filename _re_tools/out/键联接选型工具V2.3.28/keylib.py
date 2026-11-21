# Reconstructed from bytecode by split_decompile.py
# keylib.pyc

'''我的零件库 —— SQLite 本地库（v2.3）

合规红线：
  1. 图纸只存【本机文件路径引用】+版本备注，绝不复制文件内容进库/进 EXE
  2. 库文件 keylib.db 存放在 EXE 同目录（用户本机），不打包进任何发布产物
  3. 供应商/客户联系人等个人信息仅存本机，随用户掌控
'''
import os
import sys
import shutil
import sqlite3
from datetime import datetime
DB_NAME = 'keylib.db'

def _dir_writable(d):
    '''探测目录可写（决定库文件能否放 EXE 同目录）'''

    try:
        probe = os.path.join(d, '.keylib_write_test')
        with open(probe, 'w') as f:
            f.write('t')
        os.remove(probe)
        return True
    except OSError:
        return False


def db_path():
    '''库文件位置：打包运行放 EXE 同目录（不可写则回退 ~/.KeyTool），开发时放源码目录'''
    if getattr(sys, 'frozen', False):
        p = os.path.join(os.path.dirname(sys.executable), DB_NAME)
        if not _dir_writable(os.path.dirname(p)):
            p = os.path.join(os.path.expanduser('~'), '.KeyTool', DB_NAME)
            os.makedirs(os.path.dirname(p), exist_ok=True)
    else:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)
    return p
def connect():
    conn = sqlite3.connect(db_path())
    conn.execute('PRAGMA foreign_keys = ON')
    conn.row_factory = sqlite3.Row
    _init_tables(conn)
    return conn
def _init_tables(conn):
    c = conn.cursor()
    c.executescript("\n    CREATE TABLE IF NOT EXISTS material (\n        id   INTEGER PRIMARY KEY AUTOINCREMENT,\n        name TEXT UNIQUE NOT NULL\n    );\n    CREATE TABLE IF NOT EXISTS supplier (\n        id      INTEGER PRIMARY KEY AUTOINCREMENT,\n        name    TEXT UNIQUE NOT NULL,\n        contact TEXT DEFAULT ''\n    );\n    CREATE TABLE IF NOT EXISTS customer (\n        id      INTEGER PRIMARY KEY AUTOINCREMENT,\n        name    TEXT UNIQUE NOT NULL,\n        contact TEXT DEFAULT ''\n    );\n    CREATE TABLE IF NOT EXISTS spec (\n        id          INTEGER PRIMARY KEY AUTOINCREMENT,\n        mark        TEXT NOT NULL,\n        key_type    TEXT DEFAULT '平键',\n        d  REAL NOT NULL, b REAL NOT NULL, h REAL NOT NULL,\n        t1 REAL DEFAULT 0, t2 REAL DEFAULT 0, L REAL DEFAULT 0,\n        std_ref     TEXT DEFAULT '自定义',\n        material_id INTEGER REFERENCES material(id) ON DELETE SET NULL,\n        note        TEXT DEFAULT '',\n        created_at  TEXT DEFAULT (datetime('now','localtime'))\n    );\n    CREATE TABLE IF NOT EXISTS spec_supplier (\n        spec_id     INTEGER NOT NULL REFERENCES spec(id) ON DELETE CASCADE,\n        supplier_id INTEGER NOT NULL REFERENCES supplier(id) ON DELETE CASCADE,\n        qty   TEXT DEFAULT '', price TEXT DEFAULT '',\n        date  TEXT DEFAULT '', note TEXT DEFAULT '',\n        PRIMARY KEY (spec_id, supplier_id)\n    );\n    CREATE TABLE IF NOT EXISTS spec_customer (\n        spec_id    INTEGER NOT NULL REFERENCES spec(id) ON DELETE CASCADE,\n        customer_id INTEGER NOT NULL REFERENCES customer(id) ON DELETE CASCADE,\n        qty  TEXT DEFAULT '', price TEXT DEFAULT '',\n        date TEXT DEFAULT '', note TEXT DEFAULT '',\n        PRIMARY KEY (spec_id, customer_id)\n    );\n    CREATE TABLE IF NOT EXISTS spec_drawing (\n        id      INTEGER PRIMARY KEY AUTOINCREMENT,\n        spec_id INTEGER NOT NULL REFERENCES spec(id) ON DELETE CASCADE,\n        path    TEXT NOT NULL,\n        rev     TEXT DEFAULT '',\n        note    TEXT DEFAULT ''\n    );\n    ")
    conn.commit()
def validate_spec(d, b, h, L=0, t1=0, t2=0, key_type='平键'):
    '''录入校验：返回错误信息字符串，None 表示通过。
    花键为多齿结构，键高/键长/槽深不适用，允许留空（0）；
    键高>0 与 b/h 比例检查仅对普通键（平键/楔键/半圆键）生效。'''
    for name, v in (('轴径d', d), ('键宽b', b), ('键高h', h), ('键长L', L), ('轴槽深t1', t1), ('毂槽深t2', t2)):
        try:
            v = float(v)
        except (TypeError, ValueError):
            return f'{name} 不是有效数字'
        if name in ('轴径d', '键宽b', '键高h') and v <= 0 and not (key_type == '花键' and name == '键高h'):
            return f'{name} 必须 > 0'
        if name in ('键长L', '轴槽深t1', '毂槽深t2') and v < 0:
            return f'{name} 不能为负'
    if key_type != '花键':
        if b >= h * 3:
            return '键宽 b 相对键高 h 过大，请复核'
        if L and L < b:
            return '键长 L 不应小于键宽 b，请复核'
    return None


def add_spec(conn, mark, d, b, h, L=0, t1=0, t2=0, key_type='平键', std_ref='自定义', material_id=None, note=''):
    err = validate_spec(d, b, h, L, t1, t2, key_type)
    if err:
        raise ValueError(err)
    cur = conn.execute('INSERT INTO spec(mark,key_type,d,b,h,t1,t2,L,std_ref,material_id,note) VALUES(?,?,?,?,?,?,?,?,?,?,?)', (mark, key_type, float(d), float(b), float(h), float(t1), float(t2), float(L), std_ref, material_id, note))
    conn.commit()
    return cur.lastrowid
def update_spec(conn, spec_id, **fields):
    allowed = {
        'L',
        'b',
        'd',
        'h',
        't1',
        't2',
        'mark',
        'note',
        'std_ref',
        'key_type',
        'material_id'}
    sets, vals = [], []
    for k, v in fields.items():
        if k in allowed:
            sets.append(f'''{k}=?''')
            vals.append(v)
    if sets:
        vals.append(spec_id)
        conn.execute(f'''UPDATE spec SET {', '.join(sets)} WHERE id=?''', vals)
        conn.commit()
        return None
def delete_spec(conn, spec_id):
    conn.execute('DELETE FROM spec WHERE id=?', (spec_id,))
    conn.commit()
def list_specs(conn, keyword='', key_type=''):
    """key_type 传非空时按键型过滤（'' = 全部类型）"""
    sql = 'SELECT s.*, m.name AS material_name FROM spec s LEFT JOIN material m ON m.id = s.material_id'
    conds, args = [], ()
    if keyword:
        conds.append('(s.mark LIKE ? OR s.note LIKE ? OR s.std_ref LIKE ?)')
        like = f'''%{keyword}%'''
        args = (like, like, like)
    if key_type:
        conds.append('s.key_type = ?')
        args = args + (key_type,)
    if conds:
        sql += ' WHERE ' + ' AND '.join(conds)
    sql += ' ORDER BY s.id DESC'
    return conn.execute(sql, args).fetchall()
def get_spec(conn, spec_id):
    return conn.execute('SELECT s.*, m.name AS material_name FROM spec s LEFT JOIN material m ON m.id = s.material_id WHERE s.id=?', (spec_id,)).fetchone()
def list_materials(conn):
    return [r['name'] for r in conn.execute('SELECT name FROM material ORDER BY name')]
def ensure_material(conn, name):
    name = name.strip()
    if not name:
        return None
    conn.execute('INSERT OR IGNORE INTO material(name) VALUES(?)', (name,))
    conn.commit()
    return conn.execute('SELECT id FROM material WHERE name=?', (name,)).fetchone()['id']
def _roster(conn, table):
    return conn.execute(f'''SELECT id, name, contact FROM {table} ORDER BY name''').fetchall()
def list_suppliers(conn):
    return _roster(conn, 'supplier')
def list_customers(conn):
    return _roster(conn, 'customer')
def ensure_roster(conn, table, name, contact=''):
    name = name.strip()
    if not name:
        return None
    conn.execute(f'''INSERT INTO {table}(name, contact) VALUES(?, ?) ON CONFLICT(name) DO UPDATE SET contact=excluded.contact WHERE excluded.contact != \'\'''', (name, contact))
    conn.commit()
    return conn.execute(f'''SELECT id FROM {table} WHERE name=?''', (name,)).fetchone()['id']
def delete_roster_entry(conn, table, entry_id):
    conn.execute(f'''DELETE FROM {table} WHERE id=?''', (entry_id,))
    conn.commit()
def link_partner(conn, spec_id, table, partner_id, qty='', price='', date='', note=''):
    pcol = 'supplier_id' if table == 'supplier' else 'customer_id'
    lt = f'''spec_{table}'''
    conn.execute(f'''INSERT OR REPLACE INTO {lt}(spec_id,{pcol},qty,price,date,note) VALUES(?,?,?,?,?,?)''', (spec_id, partner_id, qty, price, date, note))
    conn.commit()
def unlink_partner(conn, spec_id, table, partner_id):
    pcol = 'supplier_id' if table == 'supplier' else 'customer_id'
    conn.execute(f'''DELETE FROM spec_{table} WHERE spec_id=? AND {pcol}=?''', (spec_id, partner_id))
    conn.commit()
def list_links(conn, spec_id, table):
    pcol = 'supplier_id' if table == 'supplier' else 'customer_id'
    lt = f'''spec_{table}'''
    return conn.execute(f'''SELECT l.{pcol} AS pid, p.name, p.contact, l.qty, l.price, l.date, l.note FROM {lt} l JOIN {table} p ON p.id = l.{pcol} WHERE l.spec_id = ? ORDER BY p.name''', (spec_id,)).fetchall()
def who_uses(conn, table, partner_id):
    '''反向查询：某供应商/客户关联了哪些规格'''
    pcol = 'supplier_id' if table == 'supplier' else 'customer_id'
    return conn.execute(f'''SELECT s.* FROM spec_{table} l JOIN spec s ON s.id = l.spec_id WHERE l.{pcol} = ? ORDER BY s.mark''', (partner_id,)).fetchall()
def add_drawing(conn, spec_id, path, rev='', note=''):
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f'''图纸文件不存在：{path}''')
    cur = conn.execute('INSERT INTO spec_drawing(spec_id,path,rev,note) VALUES(?,?,?,?)', (spec_id, path, rev, note))
    conn.commit()
    return cur.lastrowid
def list_drawings(conn, spec_id):
    return conn.execute('SELECT * FROM spec_drawing WHERE spec_id=? ORDER BY id', (spec_id,)).fetchall()
def delete_drawing(conn, drawing_id):
    conn.execute('DELETE FROM spec_drawing WHERE id=?', (drawing_id,))
    conn.commit()
def open_drawing(path):
    '''用系统默认程序打开图纸（只引用本机文件）'''
    if not os.path.exists(path):
        raise FileNotFoundError(f'''图纸文件已移动或删除：{path}''')
    os.startfile(path)
def export_csv(conn, out_path):
    '''导出规格清单及关联摘要为 CSV（UTF-8 BOM，Excel 直开）'''
    rows = ['标记,键型,d,b,h,t1,t2,L,参照标准,材料,备注,供应商,客户,图纸数']
    for s in list_specs(conn):
        sup = '; '.join(r['name'] for r in list_links(conn, s['id'], 'supplier'))
        cus = '; '.join(r['name'] for r in list_links(conn, s['id'], 'customer'))
        ndwg = len(list_drawings(conn, s['id']))

        def esc(v):
            v = '' if v is None else str(v)
            return '"' + v.replace('"', '""') + '"' if any(ch in v for ch in ',"\n') else v
        rows.append(','.join(esc(x) for x in (s['mark'], s['key_type'], s['d'], s['b'], s['h'], s['t1'], s['t2'], s['L'], s['std_ref'], s['material_name'], s['note'], sup, cus, ndwg)))
    with open(out_path, 'w', encoding='utf-8-sig', newline='') as f:
        f.write('\n'.join(rows))
    return len(rows) - 1
def backup_db(conn, dest):
    '''在线备份（不中断连接）'''
    dest_conn = sqlite3.connect(dest)
    conn.backup(dest_conn)
    dest_conn.close()
    return os.path.getsize(dest)
def restore_db(dest_path):
    '''用备份文件覆盖当前库（调用方负责确认）'''
    if not os.path.exists(dest_path):
        raise FileNotFoundError(dest_path)
    shutil.copy2(dest_path, db_path())
def stats(conn):
    return {
        'specs': conn.execute('SELECT COUNT(*) c FROM spec').fetchone()['c'],
        'suppliers': conn.execute('SELECT COUNT(*) c FROM supplier').fetchone()['c'],
        'customers': conn.execute('SELECT COUNT(*) c FROM customer').fetchone()['c'],
        'materials': conn.execute('SELECT COUNT(*) c FROM material').fetchone()['c'],
        'drawings': conn.execute('SELECT COUNT(*) c FROM spec_drawing').fetchone()['c'] }

