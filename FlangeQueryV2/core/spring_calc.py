# Source Generated with Decompyle++
# Decompiled by MUHAMMAD SHAKIB
# GitHub: https://github.com/0xSHAK1B
# File: spring_calc.pyc (Python 3.11)

'''弹簧设计计算（GB/T 23935-2009 圆柱螺旋弹簧）。

当前实现：
· 压缩弹簧完整设计（选 d、D、n，校核切应力、稳定性、疲劳）
· 拉伸弹簧简化校核（按压缩弹簧公式，忽略初拉力精细项）
· 扭转弹簧弯曲应力校核

所有公式只落数值关系与标准号，不复制原文。
'''
import math
from .spring_data import get_Rm, recommend_C, allowable_stress

def _K(C):
    '''曲度系数 K = (4C-1)/(4C-4) + 0.615/C。'''
    return (4 * C - 1) / (4 * C - 4) + 0.615 / C


def _available_diameters(material):
    pts = set()
    for dmin, dmax, _ in material['ranges']:
        pts.add(round(dmin, 3))
        pts.add(round(dmax, 3))
    return sorted(pts)


def _round_up_d(d_req, available):
    '''选不小于需求的最小标准线径。'''
    for d in available:
        if d >= d_req - 1e-06:
            return d
    return available[-1]


def _tau(D, d, F, K = None):
    K = K or _K(D / d)
    return K * 8 * D * F / (math.pi * d ** 3)


def _stiffness(G, d, D, n):
    return G * d ** 4 / (8 * D ** 3 * n)


def _spring_rate_from_loads(F2, F1, f2, f1):
    '''刚度 = ΔF / Δf。'''
    return (F2 - F1) / (f2 - f1)


class InputError(ValueError):
    '''输入参数不合理（非计算失败）。UI 需据此拒绝出结论。'''
    pass


def _check_common(F_big, F_small, what_big, what_small, delta_name):
    '''通用校验：负值、大小关系、行程/角度为正。返回 (delta,)。'''
    for name, v in ((what_big, F_big), (what_small, F_small)):
        if v is None or isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            raise InputError(f'''{name} 不是有效数值''')
        if v < 0:
            raise InputError(f'''{name} = {v:g} 不应为负值''')
    if F_big <= 0:
        raise InputError(f'''{what_big} = {F_big:g} 应大于 0''')
    if F_small > F_big:
        raise InputError(f'''{what_small}({F_small:g}) 不应大于 {what_big}({F_big:g})''')
    return F_big - F_small


def design_compression(F2, F1, stroke, material, load_type, C_user, Dmax, use_high_allow, allow_factor = 1.0):
    '''压缩弹簧设计计算。

      allow_factor  许用应力折减系数（拉伸弹簧按 GB/T 23935-2009 5.3.2 取 0.80）

    输入：
      F2          最大工作负荷 N
      F1          最小工作负荷 N（可=0）
      stroke      工作行程 mm（= f2 - f1）
      material    spring_data.MATERIALS 中的一项
      load_type   static/finite/infinite/test
      C_user      用户指定旋绕比（None 则按推荐中值）
      Dmax        允许最大外径 mm（None 不限制）
    返回 dict（包含 d, D, n, 刚度, τmax, 安全系数, 稳定性提示等）
    '''
    _check_common(F2, F1, '最大工作负荷 F2', '最小工作负荷 F1', '负荷差')
    if stroke is None or stroke <= 0:
        raise InputError(f'''工作行程 stroke = {stroke:g} 应大于 0''')
    if F2 - F1 <= 0:
        raise InputError('F2 与 F1 相等时无法确定有效圈数，请给出有效行程下的负荷差')
    G = material['G']
    kind = material['kind']
    Rm = get_Rm(material, 2.0)
    tau_allow = Rm * allowable_stress(kind, 'torsion', load_type, use_high = use_high_allow) * allow_factor
    available_d = _available_diameters(material)
    d0 = 2.0
    (C_lo, C_hi) = recommend_C(d0)
    C = C_user if C_user else (C_lo + C_hi) / 2
    K = _K(C)
    d_req = (8 * K * C * F2 / (math.pi * tau_allow)) ** 0.5
    d = _round_up_d(d_req, available_d)
    (C_lo, C_hi) = recommend_C(d)
    C = C_user if C_user else (C_lo + C_hi) / 2
    if Dmax is not None:
        C_max = Dmax / d - 1
        if C > C_max:
            C = max(4.0, C_max)
    Rm = get_Rm(material, d)
    tau_allow = Rm * allowable_stress(kind, 'torsion', load_type, use_high = use_high_allow) * allow_factor
    K = _K(C)
    d_req = (8 * K * C * F2 / (math.pi * tau_allow)) ** 0.5
    d = _round_up_d(d_req, available_d)
    if C_user is None:
        (C_lo, C_hi) = recommend_C(d)
        C = (C_lo + C_hi) / 2
        if Dmax is not None:
            C_max = Dmax / d - 1
            if C > C_max:
                C = max(4.0, C_max)
        K = _K(C)
    D = C * d
    Rm = get_Rm(material, d)
    tau_allow = Rm * allowable_stress(kind, 'torsion', load_type, use_high = use_high_allow) * allow_factor
    delta_F = F2 - F1
    n_raw = G * d ** 4 * stroke / (8 * D ** 3 * delta_F)
    n = max(2.0, math.ceil(n_raw * 2) / 2)
    k = _stiffness(G, d, D, n)
    tau_max = _tau(D, d, F2, K)
    tau_min = _tau(D, d, F1, K) if F1 > 0 else 0.0
    safety = tau_allow / tau_max if tau_max > 0 else float('inf')
    fatigue_safety = None
    tau_u0 = None
    tau_amp = None
    S_min = 1.1
    if load_type in ('finite', 'infinite'):
        tau_u0 = Rm * (0.32 if load_type == 'finite' else 0.3) * allow_factor
        tau_amp = tau_max - tau_min
        fatigue_safety = (tau_u0 + 0.75 * tau_min) / tau_max if tau_max > 0 else float('inf')
    n1 = n + 2
    f2 = F2 / k
    clearance = max(0.1 * d, (0.5 * d + 0.1 * f2) / n)
    pitch = d + f2 / n + clearance
    H0 = n * pitch + 1.5 * d
    Hb = n1 * d
    f_max = H0 - Hb
    tau_s = Rm * allowable_stress(kind, 'torsion', 'test', use_high = False) * allow_factor
    Fs = tau_s * math.pi * d ** 3 / (8 * K * D) if K * D > 0 else float('inf')
    fs = Fs / k
    work_ratio = f2 / fs if fs > 0 else float('inf')
    slenderness = H0 / D
    stability_note = ''
    if slenderness > 5.3:
        stability_note = f'''高径比 b=H0/D={slenderness:.2f}：超出两端固定允许的 5.3（一端固定一端回转 3.7、两端回转 2.6，GB/T 23935 6.5.2.1），建议加导杆/导套或改参数；本工具未做临界负荷 Fc 校核'''
    elif slenderness > 3.7:
        stability_note = f'''高径比 b=H0/D={slenderness:.2f}：超出一端固定一端回转允许的 3.7（两端回转 2.6，GB/T 23935 6.5.2.1），请按实际支承条件确认；本工具未做临界负荷 Fc 校核'''
    elif slenderness > 2.6:
        stability_note = f'''高径比 b=H0/D={slenderness:.2f}：超出两端回转允许的 2.6（GB/T 23935 6.5.2.1），请按实际支承条件确认'''
    elif slenderness < 0.8:
        stability_note = f'''高径比 b=H0/D={slenderness:.2f} 低于 0.8（GB/T 23935 6.5.2.3），稳定性不利'''
    geometry_notes = []
    if f2 > f_max:
        geometry_notes.append(f'''自由高度不足：达到 F2 需变形 {f2:.2f} mm，但可压缩量仅 {f_max:.2f} mm（压并高度 {Hb:.2f} mm），弹簧在到达 F2 前已压并''')
    elif f2 > f_max * 0.95:
        geometry_notes.append(f'''余量偏紧：F2 下变形 {f2:.2f} mm，可压缩量 {f_max:.2f} mm，建议加大自由高度''')
    if fs > 0:
        if work_ratio > 0.8:
            geometry_notes.append(f'''工作变形量 f2={f2:.2f} mm 超过试验变形量 fs 的 80%（{0.8 * fs:.2f} mm），超出 GB/T 23935 推荐工作区间 0.2fs~0.8fs''')
        elif work_ratio < 0.2:
            geometry_notes.append(f'''工作变形量 f2={f2:.2f} mm 低于试验变形量 fs 的 20%（{0.2 * fs:.2f} mm），低于 GB/T 23935 推荐工作区间，材料利用率偏低''')
    warnings = []
    if not 0 < n <= 200:
        warnings.append(f'''有效圈数 n={n:g} 超出常规范围，结果不宜直接采用''')
    if not 0 < H0 < 10000.0:
        warnings.append(f'''自由高度 H0={H0:g} mm 超出常规范围，结果不宜直接采用''')
    if not 0 < D < 10000.0:
        warnings.append(f'''中径 D={D:.2f} mm 超出常规范围，结果不宜直接采用''')
    c_note = ''
    (C_lo_tab, C_hi_tab) = recommend_C(d)
    if not (C_lo_tab <= C <= C_hi_tab):
        c_note = f'''旋绕比 C={C:.2f} 落在 d={d:g} mm 的推荐范围 {C_lo_tab}~{C_hi_tab} 之外{'（用户指定值）' if C_user else '（受外径约束压缩）'}，工艺性与稳定性需另行确认'''
    fatigue_note = ''
    if load_type in ('finite', 'infinite'):
        if tau_max - tau_min <= 1e-06:
            fatigue_note = '应力幅接近 0，本次疲劳校核不适用（F1 与 F2 差值过小）'
        elif fatigue_safety is not None and math.isinf(fatigue_safety):
            fatigue_note = '疲劳安全系数计算溢出，疲劳校核不适用'
    return {
        'type': 'compression',
        'd': d,
        'D': D,
        'C': C,
        'n': n,
        'n1': n1,
        'k': k,
        'F2': F2,
        'F1': F1,
        'stroke': stroke,
        'f2': F2 / k,
        'f1': F1 / k,
        'H0': H0,
        'pitch': pitch,
        'clearance': clearance,
        'Hb': Hb,
        'f_max': f_max,
        'Fs': Fs,
        'fs': fs,
        'work_ratio': work_ratio,
        'geometry_notes': geometry_notes,
        'tau_max': tau_max,
        'tau_min': tau_min,
        'tau_allow': tau_allow,
        'safety': safety,
        'fatigue_safety': fatigue_safety,
        'tau_u0': tau_u0,
        'tau_amp': tau_amp,
        'S_min': S_min,
        'fatigue_basis': f'''Sf = (τu0 + 0.75 τmin) / τmax（GB/T 23935-2009 6.5.1 公式30）；τu0 = {'0.32' if load_type == 'finite' else '0.30'} × σb''' + (f''' × {allow_factor:g}''' if allow_factor != 1.0 else '') + '（表9：有限寿命取 N=10⁶ 档下限，无限寿命 N≥10⁷）。' + '未计入喷丸强化与表面状态影响；重要用途弹簧建议做试验验证',
        'slenderness': slenderness,
        'stability_note': stability_note,
        'c_note': c_note,
        'warnings': warnings,
        'fatigue_note': fatigue_note,
        'coeff': allowable_stress(kind, 'torsion', load_type, use_high = use_high_allow) * allow_factor,
        'allow_factor': allow_factor,
        'allow_basis': 'GB/T 23935-2009 表3（冷卷压缩弹簧切应力）',
        'end_type_note': '端部结构按两端圈磨平、支承圈数 nZ=2 计（GB/T 23935 表8：总圈数 n1=n+2，自由高度 H0=n·t+1.5d）',
        'G': G,
        'E': material['E'],
        'Rm': Rm,
        'material': material['name'],
        'load_type': load_type }


def design_tension(F2, F1, stroke, material, load_type, C_user, Dmax, use_high_allow = ('static', None, None, False)):
    '''拉伸弹簧设计（切应力公式与压缩弹簧相同）。

    许用应力：GB/T 23935-2009 5.3.2「冷卷拉伸弹簧的试验切应力及许用切应力，
    取表 3 所列值的 80%」，故本工具对拉伸按 0.80 折减（含试验应力与疲劳幅基准）。
    未计入项：初拉力 F0、钩环处应力集中 —— 使用中需另行处理。
    '''
    res = design_compression(F2, F1, stroke, material, load_type, C_user, Dmax, use_high_allow, allow_factor = 0.8)
    res['type'] = 'tension'
    res['stability_note'] = ''
    res['slenderness'] = None
    res['allow_basis'] = 'GB/T 23935-2009 表3 × 0.80（5.3.2：冷卷拉伸弹簧许用切应力取表3值的 80%）'
    res['end_type_note'] = ''
    res['tension_note'] = '初拉力 F0 与钩环处应力集中本工具未计入，钩环强度与初拉力需按 GB/T 23935 相关条款另行校核'
    res['pitch'] = res['d']
    res['clearance'] = 0.0
    res['H0'] = res['n1'] * res['d']
    res['Hb'] = None
    res['f_max'] = None
    res['geometry_notes'] = [n for n in res['geometry_notes'] if '工作区间' in n]
    res['H0_note'] = '自由长度为并紧估算值，未含钩环轴向尺寸'
    return res


def design_torsion(M2, M1, angle, material, load_type, C_user, Dmax, use_high_allow = ('static', None, None, False)):
    '''扭转弹簧弯曲应力校核（GB/T 23935-2009 第8章）。

    M2, M1 单位为 N·mm；angle 为工作扭转角 °。
    '''
    G = material['G']
    E = material['E']
    kind = material['kind']
    available_d = _available_diameters(material)
    Rm = get_Rm(material, 2.0)
    sigma_allow = Rm * allowable_stress(kind, 'bending', load_type, use_high = use_high_allow)
    d0 = 2.0
    (C_lo, C_hi) = recommend_C(d0)
    C = C_user if C_user else (C_lo + C_hi) / 2
    if Dmax is not None:
        C_max = Dmax / d0 - 1
        if C > C_max:
            C = max(4.0, C_max)
    K1 = (4 * C ** 2 - C - 1) / (4 * C * (C - 1))
    d_req = (32 * K1 * M2 / (math.pi * sigma_allow)) ** 0.3333333333333333
    d = _round_up_d(d_req, available_d)
    if C_user is None:
        (C_lo, C_hi) = recommend_C(d)
        C = (C_lo + C_hi) / 2
        if Dmax is not None:
            C_max = Dmax / d - 1
            if C > C_max:
                C = max(4.0, C_max)
    D = C * d
    K1 = (4 * C ** 2 - C - 1) / (4 * C * (C - 1))
    Rm = get_Rm(material, d)
    sigma_allow = Rm * allowable_stress(kind, 'bending', load_type, use_high = use_high_allow)
    d_req = (32 * K1 * M2 / (math.pi * sigma_allow)) ** 0.3333333333333333
    d = _round_up_d(d_req, available_d)
    D = C * d
    K1 = (4 * C ** 2 - C - 1) / (4 * C * (C - 1))
    delta_M = _check_common(M2, M1, '最大扭矩 M2', '最小扭矩 M1', '扭矩差')
    if angle is None or angle <= 0:
        raise InputError(f'''工作扭转角 angle = {angle:g} 应大于 0''')
    if delta_M <= 0:
        raise InputError('M2 与 M1 相等时无法确定有效圈数，请给出有效扭矩差')
    n_raw = E * d ** 4 * angle / (3667 * D * delta_M)
    n = max(2.0, math.ceil(n_raw * 2) / 2)
    angle_actual = 3667 * D * delta_M * n / (E * d ** 4)
    k_torque_actual = delta_M / angle_actual if angle_actual > 0 else float('inf')
    sigma_max = K1 * 32 * M2 / (math.pi * d ** 3)
    sigma_min = K1 * 32 * M1 / (math.pi * d ** 3) if M1 > 0 else 0.0
    safety = sigma_allow / sigma_max if sigma_max > 0 else float('inf')
    fatigue_safety = None
    sigma_allow_amp = None
    sigma_amp = None
    if load_type in ('finite', 'infinite'):
        sigma_allow_amp = Rm * allowable_stress(kind, 'bending', load_type, use_high = False)
        sigma_amp = sigma_max - sigma_min
        fatigue_safety = sigma_allow_amp / sigma_amp if sigma_amp > 0 else float('inf')
    sigma_s = Rm * allowable_stress(kind, 'bending', 'test', use_high = False)
    Ts = math.pi * d ** 3 * sigma_s / 32
    T_rate = k_torque_actual
    phi_s = Ts / T_rate if T_rate > 0 else float('inf')
    ts_notes = []
    if Ts > 0:
        if M2 > 0.8 * Ts:
            ts_notes.append(f'''最大工作扭矩 M2={M2:.0f} N·mm 超过试验扭矩 Ts 的 80%（{0.8 * Ts:.0f} N·mm），超出 GB/T 23935 8.2 推荐工作区间 0.2Ts~0.8Ts''')
        elif M2 < 0.2 * Ts:
            ts_notes.append(f'''最大工作扭矩 M2={M2:.0f} N·mm 低于试验扭矩 Ts 的 20%（{0.2 * Ts:.0f} N·mm），低于 GB/T 23935 8.2 推荐工作区间，材料利用率偏低''')
    arm_limit = 0.09 * math.pi * D * n
    arm_note = f'''未输入扭臂长度：当 l1+l2 ≥ 0.09πDn = {arm_limit:.1f} mm 时，须按公式(53)/(54)计入扭臂变形（GB/T 23935 8.1.2.2）'''
    warnings = []
    if not 0 < n <= 200:
        warnings.append(f'''有效圈数 n={n:g} 超出常规范围，结果不宜直接采用''')
    (C_lo_tab, C_hi_tab) = recommend_C(d)
    c_note = ''
    if not C_lo_tab <= C <= C_hi_tab:
        c_note = f'''旋绕比 C={C:.2f} 落在 d={d:g} mm 的推荐范围 {C_lo_tab}~{C_hi_tab} 之外{'（用户指定值）' if C_user else '（受外径约束压缩）'}，工艺性需另行确认'''
    fatigue_note = ''
    if load_type in ('finite', 'infinite'):
        if sigma_max - sigma_min <= 1e-06:
            fatigue_note = '应力幅接近 0，本次疲劳校核不适用（M1 与 M2 差值过小）'
        elif fatigue_safety is not None and math.isinf(fatigue_safety):
            fatigue_note = '疲劳安全系数计算溢出，疲劳校核不适用'
    return {
        'type': 'torsion',
        'd': d,
        'D': D,
        'C': C,
        'n': n,
        'k_torque': delta_M / angle,
        'k_torque_actual': k_torque_actual,
        'angle_actual': angle_actual,
        'angle_note': '工作扭转角指 M1→M2 区间内的转角（非总转角）',
        'M2': M2,
        'M1': M1,
        'angle': angle,
        'sigma_max': sigma_max,
        'sigma_min': sigma_min,
        'sigma_allow': sigma_allow,
        'safety': safety,
        'fatigue_safety': fatigue_safety,
        'sigma_allow_amp': sigma_allow_amp,
        'sigma_amp': sigma_amp,
        'fatigue_basis': f'''GB/T 23935-2009 8.4 规定扭转弹簧疲劳极限由图2查取，标准未给闭式公式；本工具不做图2插值，此处按 许用应力幅基准 / 实际应力幅 给出保守估算，基准 = σb × {allowable_stress(kind, 'bending', load_type, use_high = False)}（表4 该档下限）。未计入喷丸强化与表面状态影响''',
        'Ts': Ts,
        'phi_s': phi_s,
        'ts_notes': ts_notes,
        'arm_note': arm_note,
        'c_note': c_note,
        'warnings': warnings,
        'fatigue_note': fatigue_note,
        'coeff': allowable_stress(kind, 'bending', load_type, use_high = use_high_allow),
        'allow_basis': 'GB/T 23935-2009 表4（冷卷扭转弹簧弯曲应力）',
        'G': G,
        'E': E,
        'Rm': Rm,
        'material': material['name'],
        'load_type': load_type }

