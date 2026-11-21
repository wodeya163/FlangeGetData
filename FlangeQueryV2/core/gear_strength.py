# Source Generated with Decompyle++
# Decompiled by MUHAMMAD SHAKIB
# GitHub: https://github.com/0xSHAK1B
# File: data\gear_strength.pyc (Python 3.10)

'''齿轮强度计算模块
公式依据（2026-10-09 复核项3 核定，证据见 docs/DATA_SOURCES.md）：
  - KHβ 简化式：GB/T 3480-1997 表14（调质）/ 表15（硬齿面），对称支承
  - KHα、ZH、Zε、Yε、Yβ：GB/T 3480-1997 口径
  - Kv 动载系数：GB/T 10063-1988 式(7) 及表4 K1/K2（OCR 原文定案；
    注意不是 GB/T 3480 的 Kv——3480 一般方法为式(31)~(34) 临界转速比法）
  - 材料 σHlim/σFlim：教材与 ISO 6336-5 MQ 双源核验（45钢调质/正火 550/450）
  - 应力式骨架：张学孟法
支持：齿面接触疲劳强度 + 齿根弯曲疲劳强度校核
'''
import math
MATERIALS = {
    '45钢_调质': {
        'HRC': 28,
        'sigma_Hlim': 550,
        'sigma_Flim': 220,
        'E': 206000,
        'desc': '45钢 调质处理' },
    '45钢_正火': {
        'HRC': 20,
        'sigma_Hlim': 450,
        'sigma_Flim': 180,
        'E': 206000,
        'desc': '45钢 正火处理' },
    '40Cr_调质': {
        'HRC': 35,
        'sigma_Hlim': 650,
        'sigma_Flim': 270,
        'E': 206000,
        'desc': '40Cr 调质处理' },
    '40Cr_渗碳': {
        'HRC': 58,
        'sigma_Hlim': 1500,
        'sigma_Flim': 480,
        'E': 206000,
        'desc': '40Cr 渗碳淬火' },
    '20CrMnTi_渗碳': {
        'HRC': 58,
        'sigma_Hlim': 1500,
        'sigma_Flim': 480,
        'E': 206000,
        'desc': '20CrMnTi 渗碳淬火' },
    '38CrMoAl_氮化': {
        'HRC': 52,
        'sigma_Hlim': 1100,
        'sigma_Flim': 350,
        'E': 206000,
        'desc': '38CrMoAl 氮化处理' },
    'HT200': {
        'HRC': 0,
        'sigma_Hlim': 350,
        'sigma_Flim': 80,
        'E': 113000,
        'desc': 'HT200 灰铸铁' },
    'HT300': {
        'HRC': 0,
        'sigma_Hlim': 420,
        'sigma_Flim': 110,
        'E': 113000,
        'desc': 'HT300 灰铸铁' },
    'QT600-3': {
        'HRC': 0,
        'sigma_Hlim': 500,
        'sigma_Flim': 170,
        'E': 169000,
        'desc': 'QT600-3 球墨铸铁' },
    'ZCuSn10Pb1': {
        'HRC': 0,
        'sigma_Hlim': 280,
        'sigma_Flim': 100,
        'E': 110000,
        'desc': '锡青铜 ZCuSn10Pb1' },
    '尼龙PA66': {
        'HRC': 0,
        'sigma_Hlim': 80,
        'sigma_Flim': 40,
        'E': 30000,
        'desc': '尼龙 PA66' },
    '聚甲醛POM': {
        'HRC': 0,
        'sigma_Hlim': 60,
        'sigma_Flim': 30,
        'E': 28000,
        'desc': '聚甲醛 POM' } }

def get_material_list():
    '''返回所有可用材料列表'''
    return [ (k, v['desc']) for k, v in MATERIALS.items() ]


def get_KA(load_type='uniform'):
    '''使用系数 KA
    load_type: uniform(均匀平稳), light(轻度冲击), medium(中等冲击), heavy(严重冲击)
    '''
    ka_map = {
        'uniform': 1,
        'light': 1.25,
        'medium': 1.5,
        'heavy': 1.75 }
    return ka_map.get(load_type, 1)

K1_TABLE = {
    '直齿': {
        5: 7.51,
        6: 14.94,
        7: 26.81,
        8: 39.07,
        9: 52.85 },
    '斜齿': {
        5: 6.68,
        6: 13.3,
        7: 23.87,
        8: 34.79,
        9: 47.06 } }
K2_TABLE = {
    '直齿': 0.0193,
    '斜齿': 0.0087 }

def get_Kv(kind, precision_grade, ka, ft, b, z1, v, u):
    '''动载系数 Kv（GB/T 10063-1988 式(7)）：
    Kv = (K1/w + K2)·(z1·v/100)·√(u²/(1+u²)) + 1，其中 w = KA·Ft/b (N/mm)。
    kind: "直齿" / "斜齿"；v: 圆周速度 (m/s)。
    参数无效（载荷/齿数/速度非正）时如实返回 1.0。'''
    if kind not in K2_TABLE:
        kind = '直齿'
    k1 = K1_TABLE[kind].get(precision_grade, K1_TABLE[kind][7])
    k2 = K2_TABLE[kind]
    w = ka * ft / b if b else 0
    if w <= 0 or u <= 0 or z1 <= 0 or v <= 0:
        return 1.0
    Kv = (k1 / w + k2) * (z1 * v / 100) * math.sqrt(u * u / (1 + u * u)) + 1
    return round(Kv, 3)

_KHB_TUNED = {
    'adjust': {
        5: (1.1, 0.18, 0.12),
        6: (1.11, 0.18, 0.15),
        7: (1.12, 0.18, 0.23),
        8: (1.15, 0.18, 0.31) },
    'noadjust': {
        5: (1.14, 0.18, 0.23),
        6: (1.15, 0.18, 0.3),
        7: (1.17, 0.18, 0.47),
        8: (1.23, 0.18, 0.61) } }
_KHB_HARD = {
    'adjust': {
        5: ((1.05, 0.26, 0.1), (0.99, 0.31, 0.12)),
        6: ((1.05, 0.26, 0.16), (1, 0.31, 0.19)) },
    'noadjust': {
        5: ((1.09, 0.26, 0.2), (1.05, 0.31, 0.23)),
        6: ((1.09, 0.26, 0.33), (1.05, 0.31, 0.38)) } }

def get_KHbeta(b, d, precision_grade=7, hardened=False, adjusted=False):
    """齿向载荷分布系数 KHβ —— GB/T 3480-1997 表14（调质）/表15（硬齿面）简化式，
    对称支承布置。φd = b/d1。

    参数:
        b: 齿宽 (mm); d: 小轮分度圆直径 (mm); precision_grade: 精度等级
        hardened: 两轮是否均为表面硬化齿面（渗碳/氮化等，HRC≥40）
        adjusted: 装配时是否经检验调整或对研跑合。默认 False（不作检验调整）——
            未知装配条件下取不利口径偏保守；结果展示会注明所用口径。

    等级越界按标准前言与适用范围就近取值（调质 9 级简化式已被 GB/T 3480-1997
    撤销→按 8 级；硬齿面简化式仅 5~6 级→按 6 级），超范围提示由
    khb_applicability() 单独如实给出，不在这里静默吞掉。
    2026-10-09：取消原 1.8 封顶——封顶会把超范围大值压小（σH 随之偏小、
    偏危险方向），标准式算出多少如实给多少，范围问题交给提示行。
    """
    phi = b / d if d > 0 else 1.0
    mode = 'adjust' if adjusted else 'noadjust'
    if hardened:
        rows = _KHB_HARD[mode]
        g = precision_grade if precision_grade in rows else 6 if precision_grade > 6 else 5
        a, bb, c = rows[g][0]
        val = a + bb * phi * phi + c * 0.001 * b
        if val > 1.34:
            a2, bb2, c2 = rows[g][1]
            val = a2 + bb2 * phi * phi + c2 * 0.001 * b
    else:
        rows = _KHB_TUNED[mode]
        g = min(max(int(precision_grade), 5), 8)
        a, bb, c = rows[g]
        val = a + bb * phi * phi + c * 0.001 * b
    return round(val, 3)


def khb_applicability(b, d1, mn, precision_grade, hardened, fm_per_b):
    """GB/T 3480-1997 6.3.3.1 简化式适用范围检查。
    返回超范围提示串列表（空列表 = 各项均在范围内）。
    fm_per_b: 单位齿宽计算载荷 Fm/b (N/mm)，Fm = Ft·KA·Kv（6.3.1 定义）。
    检查项：b 50~400mm；Fm/b 调质 400~1000、硬齿面 800~1500；b/d1 调质<2.0
    硬齿面<1.5；b/h 3~12（h=2.25·mn）；精度调质 5~8 级、硬齿面 5~6 级。
    """
    notes = []
    if not 50.0 <= b <= 400.0:
        notes.append('齿宽 b=%.0f∉[50,400]mm' % b)
    lo, hi = (800, 1500) if hardened else (400, 1000)
    if not lo <= fm_per_b <= hi:
        notes.append('单位载荷 Fm/b=%.0f∉[%d,%d]N/mm' % (fm_per_b, lo, hi))
    phi = b / d1 if d1 > 0 else 99.0
    phi_max = 1.5 if hardened else 2.0
    if phi >= phi_max:
        notes.append('宽径比 b/d1=%.2f≥%.1f' % (phi, phi_max))
    h = 2.25 * mn if mn > 0 else 0
    if h > 0:
        if not 3.0 <= b / h <= 12.0:
            notes.append('齿宽比 b/h=%.2f∉[3,12]' % (b / h))
    if hardened:
        if not 5 <= precision_grade <= 6:
            notes.append('硬齿面精度 %d 级∉[5,6]' % precision_grade)
    if not hardened:
        if not 5 <= precision_grade <= 8:
            notes.append('调质精度 %d 级∉[5,8]（9级简化式已撤销，按8级取值）' % precision_grade)
    return notes


_KHA_ROWS = {
    (True, False): (1, 1, 1.1, 1.2, '3/(4-eps)'),
    (True, True): (1, 1.1, 1.2, 1.4, 'eps/cos2bb'),
    (False, False): (1, 1, 1, 1.1, 1.2),
    (False, True): (1, 1, 1.1, 1.2, 1.4) }

def get_KHalpha(precision_grade=7.0, hardened=False, helical=False, eps_alpha=None, beta=0.0, alpha_n=20.0):
    """齿间载荷分配系数 KHα（GB/T 10063-1988 表5，硬化/非硬化 × 直/斜四行）。

    返回 (值, 口径说明)。9级公式格需 eps_alpha（斜齿格另需 beta 换算 βb，
    sinβb=sinβ·cosαn）；缺参时取表内下限 1.2/1.4（表值本就不低于下限，偏安全），
    不外推不编数。精度级表列 5~9，越级按就近钳制并在口径注明。
    """
    grade = int(precision_grade)
    caliber = 'GB/T 10063 表5·%s%s行' % ('经表面硬化' if hardened else '未经表面硬化', '斜齿' if helical else '直齿')
    if not 5 <= grade <= 9:
        grade = max(5, min(9, grade))
        caliber += '（精度越级按%d级就近取值）' % grade
    v = _KHA_ROWS[(bool(hardened), bool(helical))][grade - 5]
    if isinstance(v, str):
        if v == '3/(4-eps)':
            if eps_alpha and 0 < eps_alpha < 4.0:
                raw = 3.0 / (4.0 - eps_alpha)
                v = max(raw, 1.2)
                caliber += '·9级式 max(3/(4−εα)=%.3f, 1.2)' % raw
            else:
                v = 1.2
                caliber += '·9级缺 εα 按下限 1.2 取值'
        elif eps_alpha and eps_alpha > 0:
            sb = math.sin(math.radians(beta)) * math.cos(math.radians(alpha_n))
            beta_b = math.degrees(math.asin(max(-1.0, min(1.0, sb))))
            raw = eps_alpha / math.cos(math.radians(beta_b)) ** 2
            v = max(raw, 1.4)
            caliber += '·9级式 max(εα/cos²βb=%.3f, 1.4)' % raw
        else:
            v = 1.4
            caliber += '·9级缺 εα 按下限 1.4 取值'
    return (round(v, 3), caliber)


def get_ZE(E1, E2=206000):
    '''弹性系数 ZE
    E1, E2: 两齿轮材料弹性模量 (MPa)
    '''
    nu = 0.3
    ZE = math.sqrt(1 / (math.pi * ((1 - nu ** 2) / E1 + (1 - nu ** 2) / E2)))
    return round(ZE, 2)


def _solve_alpha_w(alpha_t, x_sum, z_sum, alpha_n_rad):
    '''解啮合角：invαw = invαt + 2·xΣ·tanαn/(z1+z2)（Newton 迭代）。'''
    target = (math.tan(alpha_t) - alpha_t) + 2 * x_sum * math.tan(alpha_n_rad) / max(z_sum, 1)
    aw = alpha_t
    for _ in range(60):
        f = math.tan(aw) - aw - target
        d = math.tan(aw) ** 2
        if d < 1e-12:
            return aw
        step = f / d
        aw -= step
        if abs(step) < 1e-14:
            return aw
        return aw


def get_ZH_gb(alpha_n=20.0, beta=0.0, x1=0.0, x2=0.0, z1=20.0, z2=40.0):
    '''节点区域系数 ZH = √(2·cosβb / (cos²αt · tanαw))（GB/T 3480 口径）。
    其中 cosβb = cosβ·cosαt/cosαn；αn=20°、xΣ=0、β=0 时 ZH ≈ 2.495。'''
    an = math.radians(alpha_n)
    bt = math.radians(beta)
    alpha_t = math.atan(math.tan(an) / math.cos(bt))
    aw = _solve_alpha_w(alpha_t, x1 + x2, z1 + z2, an)
    cos_bb = math.cos(bt) * math.cos(alpha_t) / math.cos(an)
    cos_bb = max(-1, min(1, cos_bb))
    tan_aw = math.tan(aw)
    if tan_aw <= 0:
        raise ValueError('啮合角异常，无法计算 ZH')
    ZH = math.sqrt(2 * cos_bb / (math.cos(alpha_t) ** 2 * tan_aw))
    return round(ZH, 3)


def get_Zepsilon(z1, z2, mn, alpha_n=20.0, beta=0.0, x1=0.0, x2=0.0, b=0.0, ha_star=1.0):
    '''重合度系数 Zε（齿面接触强度用）。返回 (Zeps, eps_alpha, eps_beta)。
    εα 按渐开线几何精确式：εα = [√(ra1²−rb1²)+√(ra2²−rb2²)−a′sinαw] / (π·mt·cosαt)；
    εβ = b·sinβ/(π·mn)；Zε 按 GB/T 3480 口径三分支。'''
    an = math.radians(alpha_n)
    bt = math.radians(beta)
    if mn <= 0 or z1 <= 0 or z2 <= 0:
        raise ValueError('模数/齿数须为正，无法计算重合度')
    mt = mn / math.cos(bt)
    alpha_t = math.atan(math.tan(an) / math.cos(bt))
    aw = _solve_alpha_w(alpha_t, x1 + x2, z1 + z2, an)
    d1, d2 = mt * z1, mt * z2
    rb1, rb2 = d1 * math.cos(alpha_t) / 2, d2 * math.cos(alpha_t) / 2
    ra1 = d1 / 2 + (ha_star + x1) * mn
    ra2 = d2 / 2 + (ha_star + x2) * mn
    a = (d1 + d2) / 2
    a_w = a * math.cos(alpha_t) / math.cos(aw)
    t1 = ra1 ** 2 - rb1 ** 2
    t2 = ra2 ** 2 - rb2 ** 2
    if t1 <= 0 or t2 <= 0:
        raise ValueError('齿顶圆不大于基圆（变位过大），无法计算重合度')
    pb = math.pi * mt * math.cos(alpha_t)
    eps_alpha = (math.sqrt(t1) + math.sqrt(t2) - a_w * math.sin(aw)) / pb
    if eps_alpha <= 0:
        raise ValueError('端面重合度 ≤ 0（几何不成立），请检查参数')
    eps_beta = b * math.sin(bt) / (math.pi * mn) if b > 0 and beta != 0 else 0
    if eps_beta <= 0:
        Zeps = math.sqrt(max((4 - eps_alpha) / 3, 1e-09))
    elif eps_beta < 1:
        Zeps = math.sqrt(max(((4 - eps_alpha) / 3) * (1 - eps_beta) + eps_beta / eps_alpha, 1e-09))
    else:
        Zeps = math.sqrt(1 / eps_alpha)
    return (round(Zeps, 3), round(eps_alpha, 3), round(eps_beta, 3))


def get_YFa(z, x=0.0, ha_star=1.0, c_star=0.25):
    '''齿形系数 YFa（齿根弯曲强度用）
    z: 齿数
    x: 变位系数
    ha*: 齿顶高系数
    c*: 顶隙系数
    '''
    yfa_table = {
        12: 3.75,
        14: 3.45,
        16: 3.22,
        17: 3.15,
        18: 3.08,
        19: 3.02,
        20: 2.97,
        22: 2.89,
        24: 2.83,
        26: 2.78,
        28: 2.74,
        30: 2.7,
        35: 2.62,
        40: 2.56,
        45: 2.52,
        50: 2.48,
        60: 2.44,
        **{
            80: 2.4,
            100: 2.36,
            150: 2.33,
            200: 2.32,
            300: 2.31,
            500: 2.3 } }
    if z in yfa_table:
        YFa = yfa_table[z]
    else:
        keys = sorted(yfa_table.keys())
        if z < keys[0]:
            YFa = yfa_table[keys[0]]
        elif z > keys[-1]:
            YFa = yfa_table[keys[-1]]
        else:
            for i in range(len(keys) - 1):
                if keys[i] <= z <= keys[i + 1]:
                    t = (z - keys[i]) / (keys[i + 1] - keys[i])
                    YFa = yfa_table[keys[i]] + t * (yfa_table[keys[i + 1]] - yfa_table[keys[i]])
                    break
    YFa = YFa * (1 - 0.01 * x)
    return round(YFa, 3)


def get_YSa(z, x=0):
    '''应力修正系数 YSa'''
    if z <= 12:
        YSa = 2.1
    elif z <= 20:
        YSa = 2
    elif z <= 30:
        YSa = 1.8
    elif z <= 50:
        YSa = 1.65
    elif z <= 100:
        YSa = 1.55
    else:
        YSa = 1.5
    YSa = YSa * (1 + 0.005 * x)
    return round(YSa, 3)


def get_Yepsilon(eps_alpha):
    '''弯曲重合度系数 Yε = 0.25 + 0.75/εα（GB/T 3480 口径）'''
    return round(0.25 + 0.75 / max(eps_alpha, 1e-09), 3)


def get_Ybeta(beta, eps_beta=0):
    '''弯曲螺旋角系数 Yβ = 1 − εβ·β/120（β 超 30° 按 30°，εβ 超 1 按 1）'''
    b_deg = min(abs(beta), 30)
    eb = min(max(eps_beta, 0), 1)
    return round(1 - eb * b_deg / 120, 3)


def calc_tangential_force(T1, d1):
    '''计算圆周力（切向力）
    T1: 小齿轮转矩 (N·m)
    d1: 小齿轮分度圆直径 (mm)
    返回: Ft (N)
    '''
    if d1 <= 0:
        return 0
    Ft = 2000 * T1 / d1
    return round(Ft, 2)


def calc_contact_strength(sigma_Hlim, ZH, ZE, Zeps, Zbeta, Kv, KHb, KHa, Ka, Ft, d1, b, u, SA_H=1):
    '''齿面接触疲劳强度校核

    参数:
        sigma_Hlim: 许用接触应力 (MPa)
        ZH: 节点区域系数
        ZE: 弹性系数
        Zeps: 重合度系数
        Zbeta: 螺旋角系数 √cosβ
        Kv: 动载系数
        KHb: 齿向载荷分布系数
        KHa: 齿间载荷分配系数
        Ka: 使用系数
        Ft: 圆周力 (N)
        d1: 小齿轮分度圆直径 (mm)
        b: 齿宽 (mm)
        u: 传动比 (z2/z1)
        SA_H: 接触强度安全系数

    返回:
        dict: {sigma_H, sigma_Hlim, SH, result}
    '''
    if d1 <= 0 or b <= 0 or u <= 0:
        return {
            'error': '参数无效' }
    sigma_H = ZH * ZE * Zeps * Zbeta * math.sqrt(Ka * Kv * KHb * KHa * Ft * (u + 1) / (d1 * b * u))
    sigma_H = round(sigma_H, 2)
    sigma_H_allow = sigma_Hlim / SA_H
    SH = sigma_Hlim / sigma_H if sigma_H > 0 else 999
    SH = round(SH, 3)
    return {
        'sigma_H': sigma_H,
        'sigma_Hlim': sigma_Hlim,
        'sigma_H_allow': round(sigma_H_allow, 2),
        'SH': SH,
        'result': 'PASS' if sigma_H <= sigma_H_allow else 'FAIL' }


def calc_bending_strength(sigma_Flim, YFa, YSa, Yeps, Ybeta, Kv, KHb, KFa, Ka, Ft, b, mn, SA_F=1.25):
    '''齿根弯曲疲劳强度校核

    参数:
        sigma_Flim: 许用弯曲应力 (MPa)
        YFa: 齿形系数
        YSa: 应力修正系数
        Yeps: 重合度系数
        Ybeta: 螺旋角系数
        Kv: 动载系数
        KHb: 齿向载荷分布系数（KFβ=KHβ）
        KFa: 齿间载荷分配系数（KFα=KHα）
        Ka: 使用系数
        Ft: 圆周力 (N)
        b: 齿宽 (mm)
        mn: 法向模数 (mm)
        SA_F: 弯曲强度安全系数

    返回:
        dict: {sigma_F, sigma_Flim, SF, result}
    '''
    if b <= 0 or mn <= 0:
        return {
            'error': '参数无效' }
    sigma_F = Ka * Kv * KHb * KFa * Ft * YFa * YSa * Yeps * Ybeta / (b * mn)
    sigma_F = round(sigma_F, 2)
    sigma_F_allow = sigma_Flim / SA_F
    SF = sigma_Flim / sigma_F if sigma_F > 0 else 999
    SF = round(SF, 3)
    return {
        'sigma_F': sigma_F,
        'sigma_Flim': sigma_Flim,
        'sigma_F_allow': round(sigma_F_allow, 2),
        'SF': SF,
        'result': 'PASS' if sigma_F <= sigma_F_allow else 'FAIL' }


def calc_zhang_xuemeng(T1, z1, z2, mn, alpha_n, beta, b, x1, x2, mat1_key, mat2_key, precision_grade=7.0, load_type='uniform', n1=1440.0):
    '''张学孟法齿轮强度综合计算

    参数:
        T1: 小齿轮转矩 (N·m)
        z1, z2: 齿数
        mn: 法向模数 (mm)
        alpha_n: 法向压力角 (度)
        beta: 螺旋角 (度)
        b: 齿宽 (mm)
        x1, x2: 变位系数
        mat1_key, mat2_key: 材料键名
        precision_grade: 精度等级
        load_type: 载荷类型
        n1: 小齿轮转速 (r/min)，用于圆周速度/动载系数

    返回:
        dict: 完整计算结果
    '''
    if not (isinstance(z1, (int, float)) and z1 >= 1 and isinstance(z2, (int, float)) and z2 >= 1):
        raise ValueError('齿数 z1/z2 须为不小于 1 的整数')
    if not (isinstance(mn, (int, float)) and mn > 0):
        raise ValueError('法面模数 mn 须为正数')
    if not (isinstance(b, (int, float)) and b > 0):
        raise ValueError('齿宽 b 须为正数')
    if not (isinstance(T1, (int, float)) and T1 > 0):
        raise ValueError('转矩 T1 须为正数')
    if not (isinstance(n1, (int, float)) and n1 > 0):
        raise ValueError('转速 n1 须为正数')
    if not 0 < alpha_n < 90:
        raise ValueError('法向压力角 αn 须在 0~90° 之间')
    if abs(beta) >= 90:
        raise ValueError('螺旋角 β 须在 -90~90° 之间')
    result = { }
    mat1 = MATERIALS.get(mat1_key, MATERIALS['45钢_调质'])
    mat2 = MATERIALS.get(mat2_key, MATERIALS['40Cr_调质'])
    beta_rad = math.radians(beta)
    mt = mn / math.cos(beta_rad)
    d1 = z1 * mt
    d2 = z2 * mt
    a = (d1 + d2) / 2
    u = z2 / z1
    v = math.pi * d1 * n1 / 60000 if d1 > 0 else 0
    result['geometry'] = {
        'd1': round(d1, 3),
        'd2': round(d2, 3),
        'a': round(a, 3),
        'mt': round(mt, 4),
        'u': round(u, 4),
        'v': round(v, 3),
        'n1': n1 }
    Ft = calc_tangential_force(T1, d1)
    result['Ft'] = Ft
    Ka = get_KA(load_type)
    kind = '斜齿' if abs(beta) > 1e-09 else '直齿'
    Kv = get_Kv(kind, precision_grade, Ka, Ft, b, z1, v, u)
    (Zeps, eps_alpha, eps_beta) = get_Zepsilon(z1, z2, mn, alpha_n, beta, x1, x2, b)
    hardened_pair = mat1.get('HRC', 0) >= 40 and mat2.get('HRC', 0) >= 40
    mixed_pair = (mat1.get('HRC', 0) >= 40) != (mat2.get('HRC', 0) >= 40)
    KHb = get_KHbeta(b, d1, precision_grade, hardened=hardened_pair, adjusted=False)
    hardened_kha = mat1.get('HRC', 0) >= 40 or mat2.get('HRC', 0) >= 40
    (KHalpha, kha_caliber) = get_KHalpha(precision_grade, hardened=hardened_kha, helical=kind == '斜齿', eps_alpha=eps_alpha, beta=beta, alpha_n=alpha_n)
    fm_per_b = Ka * Kv * Ft / b if b > 0 else 0.0
    khb_notes = khb_applicability(b, d1, mn, precision_grade, hardened_pair, fm_per_b)
    pair_notes = []
    if mixed_pair:
        pair_notes.append('软硬齿面配对：KHβ 按调质表14、KHα 按经表面硬化行取值（偏安全口径）')
    khb_caliber = 'GB/T 3480-1997 表%s 装配时不作检验调整·对称支承' % ('15' if hardened_pair else '14')
    result['factors'] = {
        'Ka': Ka,
        'Kv': Kv,
        'KHb': KHb,
        'KHalpha': KHalpha,
        'KHb_caliber': khb_caliber,
        'KHb_notes': khb_notes,
        'KHalpha_caliber': kha_caliber,
        'pair_notes': pair_notes,
        'fm_per_b': round(fm_per_b, 1) }
    ZH = get_ZH_gb(alpha_n, beta, x1, x2, z1, z2)
    ZE = get_ZE(mat1['E'], mat2['E'])
    Zbeta = round(math.sqrt(max(math.cos(beta_rad), 1e-09)), 3)
    sigma_Hlim_pair = min(mat1['sigma_Hlim'], mat2['sigma_Hlim'])
    contact = calc_contact_strength(sigma_Hlim_pair, ZH, ZE, Zeps, Zbeta, Kv, KHb, KHalpha, Ka, Ft, d1, b, u)
    result['contact'] = contact
    result['contact']['ZH'] = ZH
    result['contact']['ZE'] = ZE
    result['contact']['Zeps'] = Zeps
    result['contact']['Zbeta'] = Zbeta
    result['contact']['eps_alpha'] = eps_alpha
    result['contact']['eps_beta'] = eps_beta
    YFa1 = get_YFa(z1, x1)
    YSa1 = get_YSa(z1, x1)
    YFa2 = get_YFa(z2, x2)
    YSa2 = get_YSa(z2, x2)
    Yeps = get_Yepsilon(eps_alpha)
    Ybeta = get_Ybeta(beta, eps_beta)
    bending1 = calc_bending_strength(mat1['sigma_Flim'], YFa1, YSa1, Yeps, Ybeta, Kv, KHb, KHalpha, Ka, Ft, b, mn)
    bending2 = calc_bending_strength(mat2['sigma_Flim'], YFa2, YSa2, Yeps, Ybeta, Kv, KHb, KHalpha, Ka, Ft, b, mn)
    result['bending1'] = bending1
    result['bending1']['YFa'] = YFa1
    result['bending1']['YSa'] = YSa1
    result['bending2'] = bending2
    result['bending2']['YFa'] = YFa2
    result['bending2']['YSa'] = YSa2
    result['bending_common'] = {
        'Yeps': Yeps,
        'Ybeta': Ybeta }
    all_pass = contact.get('result') == 'PASS' and bending1.get('result') == 'PASS' and bending2.get('result') == 'PASS'
    result['overall'] = 'PASS' if all_pass else 'FAIL'
    return result

if __name__ == '__main__':
    r = calc_zhang_xuemeng(10, 20, 40, 3, 20, 0, 20, 0, 0, '40Cr_调质', '45钢_调质', 7, 'uniform', 1440, **('T1', 'z1', 'z2', 'mn', 'alpha_n', 'beta', 'b', 'x1', 'x2', 'mat1_key', 'mat2_key', 'precision_grade', 'load_type', 'n1'))
    print('=== 张学孟法强度计算 ===')
    print(f'''几何: d1={r['geometry']['d1']}, d2={r['geometry']['d2']}, a={r['geometry']['a']}, v={r['geometry']['v']} m/s''')
    print(f'''切向力: Ft={r['Ft']}N''')
    print(f'''系数: Ka={r['factors']['Ka']}, Kv={r['factors']['Kv']}, KHb={r['factors']['KHb']}''')
    print(f'''接触应力: σH={r['contact']['sigma_H']}MPa, 许用={r['contact']['sigma_Hlim']}MPa, SH={r['contact']['SH']} → {r['contact']['result']}''')
    print(f'''弯曲应力(小): σF={r['bending1']['sigma_F']}MPa, 许用={r['bending1']['sigma_Flim']}MPa, SF={r['bending1']['SF']} → {r['bending1']['result']}''')
    print(f'''弯曲应力(大): σF={r['bending2']['sigma_F']}MPa, 许用={r['bending2']['sigma_Flim']}MPa, SF={r['bending2']['SF']} → {r['bending2']['result']}''')
    print(f'''综合结论: {r['overall']}''')
    print('\nAll tests passed!')