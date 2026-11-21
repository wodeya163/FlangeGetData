# Reconstructed from bytecode by split_decompile.py
# unit_data.pyc

'''
单位换算工具 — 数据模块
工程常用单位互转
'''
import os
import re
import json
import math
from hardness_data import convert as hardness_convert, RANGES as HARDNESS_RANGES, NAMES as HARDNESS_NAMES
CATEGORIES = {
    'length': {
        'name': '长度',
        'base': 'm',
        'units': [
            {
                'name': 'mm (毫米)',
                'factor': 0.001 },
            {
                'name': 'cm (厘米)',
                'factor': 0.01 },
            {
                'name': 'dm (分米)',
                'factor': 0.1 },
            {
                'name': 'm (米)',
                'factor': 1 },
            {
                'name': 'km (千米)',
                'factor': 1000 },
            {
                'name': 'μm (微米)',
                'factor': 1e-06 },
            {
                'name': 'in (英寸)',
                'factor': 0.0254 },
            {
                'name': 'ft (英尺)',
                'factor': 0.3048 },
            {
                'name': 'yd (码)',
                'factor': 0.9144 },
            {
                'name': 'mil (密耳)',
                'factor': 2.54e-05 },
            {
                'name': 'nm (纳米)',
                'factor': 1e-09 },
            {
                'name': 'Å (埃)',
                'factor': 1e-10 },
            {
                'name': 'nmi (海里)',
                'factor': 1852 },
            {
                'name': '里 (华里)',
                'factor': 500 }] },
    'area': {
        'name': '面积',
        'base': 'm²',
        'units': [
            {
                'name': 'mm² (平方毫米)',
                'factor': 1e-06 },
            {
                'name': 'cm² (平方厘米)',
                'factor': 0.0001 },
            {
                'name': 'dm² (平方分米)',
                'factor': 0.01 },
            {
                'name': 'm² (平方米)',
                'factor': 1 },
            {
                'name': 'km² (平方千米)',
                'factor': 1e+06 },
            {
                'name': 'in² (平方英寸)',
                'factor': 0.00064516 },
            {
                'name': 'ft² (平方英尺)',
                'factor': 0.09290304 },
            {
                'name': '亩 (中国亩)',
                'factor': 666.6667 },
            {
                'name': '公顷',
                'factor': 10000 },
            {
                'name': '英亩',
                'factor': 4046.8564 }] },
    'volume': {
        'name': '体积',
        'base': 'L',
        'units': [
            {
                'name': 'mL (毫升)',
                'factor': 0.001 },
            {
                'name': 'cm³ (立方厘米)',
                'factor': 0.001 },
            {
                'name': 'L (升)',
                'factor': 1 },
            {
                'name': 'm³ (立方米)',
                'factor': 1000 },
            {
                'name': 'in³ (立方英寸)',
                'factor': 0.016387064 },
            {
                'name': 'ft³ (立方英尺)',
                'factor': 28.316846592 },
            {
                'name': 'gal (加仑/美)',
                'factor': 3.785411784 },
            {
                'name': 'gal (加仑/英)',
                'factor': 4.54609 },
            {
                'name': 'bbl (油桶)',
                'factor': 158.987294928 },
            {
                'name': 'qt (夸脱)',
                'factor': 0.946352946 },
            {
                'name': 'pt (品脱)',
                'factor': 0.473176473 }] },
    'force': {
        'name': '力',
        'base': 'N',
        'units': [
            {
                'name': 'N (牛顿)',
                'factor': 1 },
            {
                'name': 'kN (千牛)',
                'factor': 1000 },
            {
                'name': 'MN (兆牛)',
                'factor': 1e+06 },
            {
                'name': 'kgf (千克力/公斤力)',
                'factor': 9.80665 },
            {
                'name': 'gf (克力)',
                'factor': 0.00980665 },
            {
                'name': 'lbf (磅力)',
                'factor': 4.448221615 },
            {
                'name': 'ozf (盎司力)',
                'factor': 0.27801385 }] },
    'pressure': {
        'name': '压力',
        'base': 'MPa',
        'units': [
            {
                'name': 'Pa (帕斯卡)',
                'factor': 1e-06 },
            {
                'name': 'kPa (千帕)',
                'factor': 0.001 },
            {
                'name': 'MPa (兆帕)',
                'factor': 1 },
            {
                'name': 'GPa (吉帕)',
                'factor': 1000 },
            {
                'name': 'kgf/cm² (公斤力/平方厘米)',
                'factor': 0.0980665 },
            {
                'name': 'bar (巴)',
                'factor': 0.1 },
            {
                'name': 'mbar (毫巴)',
                'factor': 0.0001 },
            {
                'name': 'psi (磅力/平方英寸)',
                'factor': 0.006894757293168361 },
            {
                'name': 'ksi (千磅力/平方英寸)',
                'factor': 6.894757293168361 },
            {
                'name': 'atm (标准大气压)',
                'factor': 0.101325 },
            {
                'name': 'mmH₂O (毫米水柱)',
                'factor': 9.80665e-06 },
            {
                'name': 'mmHg (毫米汞柱)',
                'factor': 0.0001333224 },
            {
                'name': 'inHg (英寸汞柱)',
                'factor': 0.003386389 },
            {
                'name': 'torr (托)',
                'factor': 0.0001333224 }] },
    'mass': {
        'name': '质量',
        'base': 'kg',
        'units': [
            {
                'name': 'mg (毫克)',
                'factor': 1e-06 },
            {
                'name': 'g (克)',
                'factor': 0.001 },
            {
                'name': 'kg (千克)',
                'factor': 1 },
            {
                'name': 't (吨)',
                'factor': 1000 },
            {
                'name': '斤 (市斤)',
                'factor': 0.5 },
            {
                'name': '两 (市两)',
                'factor': 0.05 },
            {
                'name': 'oz (盎司)',
                'factor': 0.028349523125 },
            {
                'name': 'lb (磅)',
                'factor': 0.45359237 },
            {
                'name': 'ton (美吨短吨)',
                'factor': 907.18474 },
            {
                'name': 'long ton (英吨长吨)',
                'factor': 1016.0469088 },
            {
                'name': 'ct (克拉)',
                'factor': 0.0002 },
            {
                'name': 'gr (格令)',
                'factor': 6.479891e-05 }] },
    'torque': {
        'name': '扭矩',
        'base': 'N·m',
        'units': [
            {
                'name': 'N·m (牛顿米)',
                'factor': 1 },
            {
                'name': 'N·mm (牛顿毫米)',
                'factor': 0.001 },
            {
                'name': 'kN·m (千牛米)',
                'factor': 1000 },
            {
                'name': 'kgf·m (千克力米)',
                'factor': 9.80665 },
            {
                'name': 'kgf·cm (千克力厘米)',
                'factor': 0.0980665 },
            {
                'name': 'kgf·mm (千克力毫米)',
                'factor': 0.00980665 },
            {
                'name': 'lbf·ft (磅力英尺)',
                'factor': 1.3558179483 },
            {
                'name': 'lbf·in (磅力英寸)',
                'factor': 0.112984829 },
            {
                'name': 'dyn·cm (达因厘米)',
                'factor': 1e-07 }] },
    'angle': {
        'name': '角度',
        'base': '°',
        'units': [
            {
                'name': '度分秒 (DMS)',
                'factor': None,
                'dms': True },
            {
                'name': '° (度)',
                'factor': 1 },
            {
                'name': '′ (角分)',
                'factor': 0.016666666666666666 },
            {
                'name': '″ (角秒)',
                'factor': 0.0002777777777777778 },
            {
                'name': 'rad (弧度)',
                'factor': 180 / math.pi },
            {
                'name': 'gon (梯度/冈)',
                'factor': 0.9 },
            {
                'name': 'rev (圈/转)',
                'factor': 360 }] },
    'density': {
        'name': '密度',
        'base': 'g/cm³',
        'units': [
            {
                'name': 'g/cm³ (克/立方厘米)',
                'factor': 1 },
            {
                'name': 'kg/m³ (千克/立方米)',
                'factor': 0.001 },
            {
                'name': 't/m³ (吨/立方米)',
                'factor': 1 },
            {
                'name': 'kg/L (千克/升)',
                'factor': 1 },
            {
                'name': 'g/mL (克/毫升)',
                'factor': 1 },
            {
                'name': 'lb/ft³ (磅/立方英尺)',
                'factor': 0.016018463 },
            {
                'name': 'lb/in³ (磅/立方英寸)',
                'factor': 27.67990471 },
            {
                'name': 'lb/gal (磅/加仑)',
                'factor': 0.119826427 }] },
    'temp': {
        'name': '温度',
        'base': '°C',
        'units': [
            {
                'name': '°C (摄氏度)',
                'factor': None },
            {
                'name': '°F (华氏度)',
                'factor': None },
            {
                'name': 'K (开尔文)',
                'factor': None }] },
    'flow': {
        'name': '流量',
        'base': 'L/min',
        'units': [
            {
                'name': 'mL/min (毫升/分)',
                'factor': 0.001 },
            {
                'name': 'L/min (升/分)',
                'factor': 1 },
            {
                'name': 'L/s (升/秒)',
                'factor': 60 },
            {
                'name': 'm³/h (立方米/时)',
                'factor': 16.666666666666668 },
            {
                'name': 'm³/min (立方米/分)',
                'factor': 1000 },
            {
                'name': 'GPM (加仑/分/美)',
                'factor': 3.785411784 },
            {
                'name': 'GPM (加仑/分/英)',
                'factor': 4.54609 },
            {
                'name': 'CFM (立方英尺/分)',
                'factor': 28.316846592 }] },
    'speed': {
        'name': '速度',
        'base': 'm/s',
        'units': [
            {
                'name': 'mm/s (毫米/秒)',
                'factor': 0.001 },
            {
                'name': 'm/s (米/秒)',
                'factor': 1 },
            {
                'name': 'm/min (米/分)',
                'factor': 0.016666666666666666 },
            {
                'name': 'km/h (千米/时)',
                'factor': 0.2777778 },
            {
                'name': 'cm/s (厘米/秒)',
                'factor': 0.01 },
            {
                'name': 'ft/s (英尺/秒)',
                'factor': 0.3048 },
            {
                'name': 'SFM (英尺/分)',
                'factor': 0.00508 },
            {
                'name': 'mph (英里/时)',
                'factor': 0.44704 },
            {
                'name': 'kn (节)',
                'factor': 0.5144444 }] },
    'tcond': {
        'name': '导热系数',
        'base': 'W/(m·K)',
        'units': [
            {
                'name': 'W/(m·K) (瓦/米开)',
                'factor': 1 },
            {
                'name': 'W/(cm·K) (瓦/厘米开)',
                'factor': 100 },
            {
                'name': 'kcal/(m·h·°C) (千卡/米时℃)',
                'factor': 1.163 },
            {
                'name': 'cal/(cm·s·°C) (卡/厘米秒℃)',
                'factor': 418.68 },
            {
                'name': 'BTU/(h·ft·°F) (英热/英尺时℉)',
                'factor': 1.730735 }] },
    'scheat': {
        'name': '比热容',
        'base': 'J/(kg·K)',
        'units': [
            {
                'name': 'J/(kg·K) (焦/千克开)',
                'factor': 1 },
            {
                'name': 'kJ/(kg·K) (千焦/千克开)',
                'factor': 1000 },
            {
                'name': 'J/(g·°C) (焦/克℃)',
                'factor': 1000 },
            {
                'name': 'cal/(g·°C) (卡/克℃)',
                'factor': 4186.8 },
            {
                'name': 'kcal/(kg·°C) (千卡/千克℃)',
                'factor': 4186.8 },
            {
                'name': 'BTU/(lb·°F) (英热/磅℉)',
                'factor': 4186.8 }] },
    'texp': {
        'name': '热膨胀系数',
        'base': '1/K',
        'units': [
            {
                'name': '10⁻⁶/°C (微米/米℃)',
                'factor': 1e-06 },
            {
                'name': '10⁻⁶/°F (微英寸/英寸℉)',
                'factor': 1.8e-06 },
            {
                'name': '10⁻⁶/K (微米/米开)',
                'factor': 1e-06 },
            {
                'name': '1/°C (每摄氏度)',
                'factor': 1 },
            {
                'name': '1/°F (每华氏度)',
                'factor': 1.8 },
            {
                'name': '1/K (每开尔文)',
                'factor': 1 }] },
    'vdyn': {
        'name': '动力粘度',
        'base': 'mPa·s',
        'units': [
            {
                'name': 'mPa·s (毫帕秒)',
                'factor': 1 },
            {
                'name': 'cP (厘泊)',
                'factor': 1 },
            {
                'name': 'Pa·s (帕秒)',
                'factor': 1000 },
            {
                'name': 'P (泊)',
                'factor': 100 },
            {
                'name': 'kgf·s/m² (千克力秒/米²)',
                'factor': 9806.65 }] },
    'vkin': {
        'name': '运动粘度',
        'base': 'mm²/s',
        'units': [
            {
                'name': 'mm²/s (二次方毫米秒)',
                'factor': 1 },
            {
                'name': 'cSt (厘斯)',
                'factor': 1 },
            {
                'name': 'St (斯)',
                'factor': 100 },
            {
                'name': 'm²/s (二次方米秒)',
                'factor': 1e+06 }] },
    **{
        'rspeed': {
            'name': '转速',
            'base': 'rpm',
            'units': [
                {
                    'name': 'rpm (转/分)',
                    'factor': 1 },
                {
                    'name': 'r/s (转/秒)',
                    'factor': 60 },
                {
                    'name': 'Hz (赫兹)',
                    'factor': 60 },
                {
                    'name': 'rad/s (弧度/秒)',
                    'factor': 60 / (2 * math.pi) }] },
        'power': {
            'name': '功率',
            'base': 'W',
            'units': [
                {
                    'name': 'mW (毫瓦)',
                    'factor': 0.001 },
                {
                    'name': 'W (瓦特)',
                    'factor': 1 },
                {
                    'name': 'kW (千瓦)',
                    'factor': 1000 },
                {
                    'name': 'MW (兆瓦)',
                    'factor': 1e+06 },
                {
                    'name': 'hp (马力)',
                    'factor': 745.69987 },
                {
                    'name': 'ps (马力/米制)',
                    'factor': 735.49875 },
                {
                    'name': 'BTU/h (英热单位/时)',
                    'factor': 0.29307107 }] },
        'energy': {
            'name': '能量',
            'base': 'J',
            'units': [
                {
                    'name': 'mJ (毫焦)',
                    'factor': 0.001 },
                {
                    'name': 'J (焦耳)',
                    'factor': 1 },
                {
                    'name': 'kJ (千焦)',
                    'factor': 1000 },
                {
                    'name': 'MJ (兆焦)',
                    'factor': 1e+06 },
                {
                    'name': 'cal (卡路里)',
                    'factor': 4.1868 },
                {
                    'name': 'kcal (千卡)',
                    'factor': 4186.8 },
                {
                    'name': 'kW·h (千瓦时/度)',
                    'factor': 3.6e+06 },
                {
                    'name': 'eV (电子伏)',
                    'factor': 1.602176634e-19 },
                {
                    'name': 'BTU (英热单位)',
                    'factor': 1055.06 }] },
        'hardness': {
            'name': '硬度',
            'base': 'HRC',
            'units': [
                {
                    'name': 'HRC (洛氏硬度)',
                    'factor': None },
                {
                    'name': 'HV (维氏硬度)',
                    'factor': None },
                {
                    'name': 'HBW (布氏硬度)',
                    'factor': None },
                {
                    'name': 'HS (肖氏硬度)',
                    'factor': None }] } } }
CAT_ORDER = [
    'length',
    'area',
    'volume',
    'mass',
    'force',
    'pressure',
    'torque',
    'angle',
    'density',
    'temp',
    'tcond',
    'scheat',
    'texp',
    'vdyn',
    'vkin',
    'rspeed',
    'speed',
    'flow',
    'power',
    'energy',
    'hardness']
CHIP_LABELS = {
    'length': '长度',
    'area': '面积',
    'volume': '体积',
    'mass': '质量',
    'force': '力',
    'pressure': '压力',
    'torque': '扭矩',
    'angle': '角度',
    'density': '密度',
    'temp': '温度',
    'tcond': '导热',
    'scheat': '比热',
    'texp': '膨胀',
    'vdyn': '动粘',
    'vkin': '运粘',
    'rspeed': '转速',
    'speed': '速度',
    **{
        'flow': '流量',
        'power': '功率',
        'energy': '能量',
        'hardness': '硬度' } }
ANGLE_DMS_IDX = 0
ANGLE_DEG_IDX = 1
_DMS_MAP = str.maketrans({
    '度': '°',
    '分': "'",
    '秒': '"',
    '′': "'",
    '‵': "'",
    '’': "'",
    '″': '"',
    '”': '"',
    'd': '°',
    'D': '°',
    'm': "'",
    'M': "'",
    's': '"',
    'S': '"' })
_DMS_FW = str.maketrans('０１２３４５６７８９．，＋－', '0123456789.,+-')

def parse_dms(text):
    '''把用户输入解析为十进制度。
    支持: 35°30\'15" / 35°30.5\' / 35d30m15s / 35 30 15 / 35.5 / 1e-3
    解析失败返回 None。负角度作用于整体（-35°30\' = -35.5°）。
    '''
    if text is None:
        return None
    t = text.strip()
    if not t:
        return None
    t = t.translate(_DMS_FW)

    try:
        return float(t)
    except ValueError:
        pass

    t = t.translate(_DMS_MAP)
    nums = re.findall('[+-]?\\d+(?:\\.\\d+)?', t)
    if not nums or len(nums) > 3:
        return None
    if len(nums) == 1 and not any(c in t for c in '°\'"'):
        return None

    try:
        d = float(nums[0])
        mnt = float(nums[1]) if len(nums) > 1 else 0.0
        sec = float(nums[2]) if len(nums) > 2 else 0.0
    except ValueError:
        return None

    if mnt >= 60 or sec >= 60:
        return None
    sign = -1.0 if d < 0 or t.lstrip().startswith('-') else 1.0
    return sign * (abs(d) + mnt / 60.0 + sec / 3600.0)
def format_dms(deg):
    '''十进制度 → 度分秒字符串，秒保留 1 位小数，进位自动归一'''
    sign = '-' if deg < 0 else ''
    a = abs(deg)
    d = int(a)
    frac = (a - d) * 60
    mnt = int(frac)
    sec = (frac - mnt) * 60
    sec = round(sec, 1)
    if sec >= 59.95:
        sec = 0
        mnt += 1
    if mnt >= 60:
        mnt = 0
        d += 1
    return '{}{}°{}′{:.1f}″'.format(sign, d, mnt, sec)
def convert(value, cat_key, from_idx, to_idx):
    '''转换单位，返回 (result, formatted_str)'''
    cat = CATEGORIES[cat_key]
    units = cat['units']
    from_u = units[from_idx]
    to_u = units[to_idx]
    if cat_key == 'temp':
        return _convert_temp(value, from_u['name'], to_u['name'])
    if cat_key == 'angle':
        base_val = value if from_idx == ANGLE_DMS_IDX else value * from_u['factor']
        if to_idx == ANGLE_DMS_IDX:
            return (base_val, format_dms(base_val))
        result = base_val / to_u['factor']
        return (result, _fmt(result))
    if cat_key == 'hardness':
        return _convert_hardness(value, from_idx, to_idx)
    base_val = value * from_u['factor']
    result = base_val / to_u['factor']
    return (result, _fmt(result))
def _convert_hardness(value, from_idx, to_idx):
    '''硬度转换（查表法）'''
    type_keys = [
        'HRC',
        'HV',
        'HBW',
        'HS']
    src = type_keys[from_idx]
    dst = type_keys[to_idx]
    results = hardness_convert(value, src)
    val = results[dst]
    if val is None:
        return (None, '无数据')
    return (val, _fmt(val))
def _convert_temp(value, from_name, to_name):
    '''温度转换（支持带中文注释的单位名）'''
    if '°C' in from_name:
        c = value
    elif '°F' in from_name:
        c = (value - 32) * 5 / 9
    elif 'K' in from_name:
        c = value - 273.15
    else:
        c = value
    if '°C' in to_name:
        r = c
    elif '°F' in to_name:
        r = c * 9 / 5 + 32
    elif 'K' in to_name:
        r = c + 273.15
    else:
        r = c
    return (r, _fmt(r))
def _fmt(val):
    '''格式化数值，始终使用小数记法，不使用科学计数法'''
    if val == 0:
        return '0'
    abs_val = abs(val)
    if abs_val >= 1e+15:
        return f'''{val:.0f}'''
    if abs_val >= 1e+12:
        return f'''{val:.1f}'''
    if abs_val >= 1e+09:
        return f'''{val:.2f}'''
    if abs_val >= 1e+06:
        return f'''{val:.3f}'''
    if abs_val >= 10000.0:
        return f'''{val:.4f}'''
    if abs_val >= 100:
        return f'''{val:.4f}'''.rstrip('0').rstrip('.')
    if abs_val >= 1:
        return f'''{val:.6f}'''.rstrip('0').rstrip('.')
    if abs_val >= 0.01:
        return f'''{val:.8f}'''.rstrip('0').rstrip('.')
    if abs_val >= 0.0001:
        return f'''{val:.10f}'''.rstrip('0').rstrip('.')
    s = f'''{val:.15f}'''.rstrip('0').rstrip('.')
    return s
_APP_DIR = os.path.join(os.path.expanduser('~'), '.UnitTool')
os.makedirs(_APP_DIR, exist_ok = True)
CONFIG_PATH = os.path.join(_APP_DIR, 'config.json')
PASSWORD_HASH = 'c76d09e61444b6081ad0adb484b2bb231acba4d1d46369ddd03598b936115b6e'

def _load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _save_config(cfg):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def _qr_path():
    if getattr(__import__('sys'), 'frozen', False):
        return os.path.join(__import__('sys')._MEIPASS, 'assets', 'qrcode.jpg')
    return os.path.join(os.path.dirname(__file__), 'assets', 'qrcode.jpg')
def is_first_run():
    return not _load_config().get('disclaimer_accepted', False)
def is_unlocked():
    return _load_config().get('unlocked', False)
THEMES = {
    'purple': {
        'label': '暗夜紫（默认）',
        'BG': '#0f0f14',
        'CARD_BG': '#1a1a24',
        'ACCENT': '#6c5ce7',
        'ACCENT_H': '#a29bfe',
        'TEXT_W': '#f0f0f0',
        'TEXT_G': '#8a8a9a',
        'BORDER': '#2a2a3a',
        'WARN': '#fdcb6e',
        'INPUT_BG': '#12121e',
        'ROW_ALT': '#151520',
        'COPIED': '#2ecc71',
        'WM': '#555566',
        'ORANGE': '#f0a050',
        'DANGER': '#ff6c6c',
        'HOVER': '#5a7ae8' },
    'blue': {
        'label': '墨蓝深空',
        'BG': '#0b1220',
        'CARD_BG': '#121d33',
        'ACCENT': '#3b82f6',
        'ACCENT_H': '#7cb7ff',
        'TEXT_W': '#e8eefc',
        'TEXT_G': '#7c8db0',
        'BORDER': '#223452',
        'WARN': '#fbbf24',
        'INPUT_BG': '#0e1728',
        'ROW_ALT': '#101b30',
        'COPIED': '#34d399',
        'WM': '#4a5a78',
        'ORANGE': '#fbbf24',
        'DANGER': '#f87171',
        'HOVER': '#2563eb' },
    'green': {
        'label': '松石暗绿',
        'BG': '#0c1412',
        'CARD_BG': '#13201b',
        'ACCENT': '#10b981',
        'ACCENT_H': '#6ee7b7',
        'TEXT_W': '#eafaf3',
        'TEXT_G': '#7fa794',
        'BORDER': '#234237',
        'WARN': '#fbbf24',
        'INPUT_BG': '#0e1a16',
        'ROW_ALT': '#10201a',
        'COPIED': '#34d399',
        'WM': '#4a6a5c',
        'ORANGE': '#f0a050',
        'DANGER': '#f87171',
        'HOVER': '#059669' },
    'red': {
        'label': '落霞红',
        'BG': '#150d10',
        'CARD_BG': '#221419',
        'ACCENT': '#e11d48',
        'ACCENT_H': '#fb7185',
        'TEXT_W': '#fbeef2',
        'TEXT_G': '#a87f8c',
        'BORDER': '#3a2230',
        'WARN': '#fbbf24',
        'INPUT_BG': '#1a0f14',
        'ROW_ALT': '#1a1116',
        'COPIED': '#34d399',
        'WM': '#6a4a55',
        'ORANGE': '#f0a050',
        'DANGER': '#fb7185',
        'HOVER': '#be123c' },
    'light': {
        'label': '暖阳米白（浅色）',
        'BG': '#f5f1e8',
        'CARD_BG': '#fffdf7',
        'ACCENT': '#d97706',
        'ACCENT_H': '#b45309',
        'TEXT_W': '#3a3226',
        'TEXT_G': '#8a7f6d',
        'BORDER': '#ddd4c2',
        'WARN': '#b45309',
        'INPUT_BG': '#fffaf0',
        'ROW_ALT': '#f7f2e7',
        'COPIED': '#059669',
        'WM': '#b0a690',
        'ORANGE': '#b45309',
        'DANGER': '#dc2626',
        'HOVER': '#92400e' } }
THEME_ORDER = [
    'purple',
    'blue',
    'green',
    'red',
    'light']
DEFAULT_THEME = 'purple'
_REQUIRED_TOKENS = ('BG', 'CARD_BG', 'ACCENT', 'ACCENT_H', 'TEXT_W', 'TEXT_G', 'BORDER', 'WARN', 'INPUT_BG', 'ROW_ALT', 'COPIED', 'WM', 'ORANGE', 'DANGER', 'HOVER')
for _k, _t in THEMES.items():
    _missing = [tok for tok in _REQUIRED_TOKENS if tok not in _t]
    assert not _missing, f'theme {_k!s} missing tokens: {_missing!s}'


def get_theme_key():
    k = _load_config().get('theme')
    return k if k in THEMES else DEFAULT_THEME


def set_theme_key(key):
    if key not in THEMES:
        return None
    cfg = _load_config()
    cfg['theme'] = key
    _save_config(cfg)
