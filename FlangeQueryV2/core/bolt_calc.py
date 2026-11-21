# Source Generated with Decompyle++
# Decompiled by MUHAMMAD SHAKIB
# GitHub: https://github.com/0xSHAK1B
# File: boltjoint_calcs_v3.pyc (Python 3.11)

'''
BoltJointTool V3 - Calculation Engine
物理模型：螺栓连接 + 螺钉连接完整校核

标准依据：
- GB/T 16823.1-1997（应力截面积 As）
- GB/T 16823.2-1997（预紧力、拧紧力矩）
- GB 50017-2017（钢结构设计标准 - 承压/剪切/撕裂）
- VDI 2230（刚度计算 Rotscher 压力锥法、载荷系数）
- 机械设计手册（成大先）螺纹连接强度校核
'''
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
BOLT_MATERIALS = {
    '4.6': {
        'name': '4.6级',
        'sigma_u': 400,
        'sigma_s': 240,
        'HRC_max': None },
    '4.8': {
        'name': '4.8级',
        'sigma_u': 420,
        'sigma_s': 340,
        'HRC_max': None },
    '5.6': {
        'name': '5.6级',
        'sigma_u': 500,
        'sigma_s': 300,
        'HRC_max': None },
    '5.8': {
        'name': '5.8级',
        'sigma_u': 520,
        'sigma_s': 420,
        'HRC_max': None },
    '6.8': {
        'name': '6.8级',
        'sigma_u': 600,
        'sigma_s': 480,
        'HRC_max': None },
    '8.8': {
        'name': '8.8级',
        'sigma_u': 830,
        'sigma_s': 660,
        'HRC_max': 32 },
    '9.8': {
        'name': '9.8级',
        'sigma_u': 900,
        'sigma_s': 720,
        'HRC_max': 35 },
    '10.9': {
        'name': '10.9级',
        'sigma_u': 1040,
        'sigma_s': 940,
        'HRC_max': 39 },
    '12.9': {
        'name': '12.9级',
        'sigma_u': 1220,
        'sigma_s': 1100,
        'HRC_max': 44 },
    'A2-50': {
        'name': 'A2-50 (304)',
        'sigma_u': 500,
        'sigma_s': 210,
        'HRC_max': None },
    'A2-70': {
        'name': 'A2-70 (304)',
        'sigma_u': 700,
        'sigma_s': 450,
        'HRC_max': None },
    'A2-80': {
        'name': 'A2-80 (304)',
        'sigma_u': 800,
        'sigma_s': 600,
        'HRC_max': None },
    'A4-70': {
        'name': 'A4-70 (316)',
        'sigma_u': 700,
        'sigma_s': 450,
        'HRC_max': None },
    'A4-80': {
        'name': 'A4-80 (316)',
        'sigma_u': 800,
        'sigma_s': 600,
        'HRC_max': None } }
PLATE_MATERIALS = {
    'Q235': {
        'name': 'Q235',
        'sigma_u': 400,
        'sigma_s': 235,
        'E': 206000,
        'mu': 0.3 },
    'Q345': {
        'name': 'Q345',
        'sigma_u': 470,
        'sigma_s': 345,
        'E': 206000,
        'mu': 0.3 },
    'Q460': {
        'name': 'Q460',
        'sigma_u': 550,
        'sigma_s': 460,
        'E': 206000,
        'mu': 0.3 },
    '20#': {
        'name': '20号钢',
        'sigma_u': 410,
        'sigma_s': 245,
        'E': 206000,
        'mu': 0.3 },
    '45#': {
        'name': '45号钢',
        'sigma_u': 600,
        'sigma_s': 355,
        'E': 206000,
        'mu': 0.3 },
    '40Cr': {
        'name': '40Cr',
        'sigma_u': 980,
        'sigma_s': 785,
        'E': 210000,
        'mu': 0.3 },
    '20CrMnTi': {
        'name': '20CrMnTi',
        'sigma_u': 1080,
        'sigma_s': 835,
        'E': 207000,
        'mu': 0.3 },
    '304': {
        'name': '304不锈钢',
        'sigma_u': 520,
        'sigma_s': 205,
        'E': 193000,
        'mu': 0.3 },
    '316': {
        'name': '316不锈钢',
        'sigma_u': 520,
        'sigma_s': 205,
        'E': 193000,
        'mu': 0.3 },
    '5052': {
        'name': '5052铝合金',
        'sigma_u': 186,
        'sigma_s': 145,
        'E': 69000,
        'mu': 0.33 },
    '6061-T6': {
        'name': '6061-T6铝合金',
        'sigma_u': 310,
        'sigma_s': 276,
        'E': 69000,
        'mu': 0.33 },
    '6063-T5': {
        'name': '6063-T5铝合金',
        'sigma_u': 186,
        'sigma_s': 145,
        'E': 69000,
        'mu': 0.33 },
    '7075-T6': {
        'name': '7075-T6铝合金',
        'sigma_u': 572,
        'sigma_s': 503,
        'E': 72000,
        'mu': 0.33 },
    'TC4': {
        'name': 'TC4钛合金',
        'sigma_u': 895,
        'sigma_s': 828,
        'E': 110000,
        'mu': 0.34 },
    'HT200': {
        'name': 'HT200铸铁',
        'sigma_u': 200,
        'sigma_s': None,
        'E': 120000,
        'mu': 0.25 },
    'HT250': {
        'name': 'HT250铸铁',
        'sigma_u': 250,
        'sigma_s': None,
        'E': 130000,
        'mu': 0.25 },
    'QT450-10': {
        'name': 'QT450-10球铁',
        'sigma_u': 450,
        'sigma_s': 310,
        'E': 170000,
        'mu': 0.28 },
    **{
        'PA66': {
            'name': 'PA66尼龙',
            'sigma_u': 85,
            'sigma_s': 82,
            'E': 3000,
            'mu': 0.4 },
        'PEEK': {
            'name': 'PEEK',
            'sigma_u': 100,
            'sigma_s': 90,
            'E': 4000,
            'mu': 0.35 } } }
FRICTION_COEFFICIENTS = {
    '喷砂-钢': {
        'mu': 0.45,
        'desc': '喷砂除锈至Sa2.5级',
        'note': '摩擦面最佳状态，预紧力传递效率最高' },
    '喷砂-铸铁': {
        'mu': 0.45,
        'desc': '喷砂除锈至Sa2.5级',
        'note': '同喷砂-钢，适用于铸铁法兰' },
    '喷砂-铝合金': {
        'mu': 0.45,
        'desc': '喷砂处理',
        'note': '铝合金结构常用' },
    '手工除锈-钢': {
        'mu': 0.3,
        'desc': '钢丝刷除锈至St3级',
        'note': '现场施工常用，摩擦力中等' },
    '手工除锈-铸铁': {
        'mu': 0.3,
        'desc': '钢丝刷除锈至St3级',
        'note': '铸铁件现场处理' },
    '手工除锈-铝合金': {
        'mu': 0.3,
        'desc': '手工打磨',
        'note': '铝合金现场处理' },
    '轧制表面-钢': {
        'mu': 0.3,
        'desc': '热轧氧化皮未处理',
        'note': '新钢材原始表面，GB 50017-2017表11.4.2-1' },
    '轧制表面-铸铁': {
        'mu': 0.3,
        'desc': '铸造表面未处理',
        'note': '铸件原始表面' },
    '轧制表面-铝合金': {
        'mu': 0.3,
        'desc': '挤压/轧制表面',
        'note': '铝型材原始表面' },
    '涂富锌漆-钢': {
        'mu': 0.35,
        'desc': '喷涂富锌底漆',
        'note': '防腐要求高时使用' },
    '涂防锈漆-钢': {
        'mu': 0.15,
        'desc': '喷涂普通防锈漆',
        'note': '摩擦系数较低，需校核' },
    '无处理-钢': {
        'mu': 0.15,
        'desc': '未做表面处理',
        'note': '摩擦系数最低，不推荐' } }
BOLT_SIZES = {
    'M3': {
        'd': 3,
        'P': 0.5,
        'd2': 2.675,
        'd3': 2.459,
        'As': 5.03,
        'dw': 6,
        'dh': 3.4 },
    'M4': {
        'd': 4,
        'P': 0.7,
        'd2': 3.545,
        'd3': 3.242,
        'As': 8.78,
        'dw': 8,
        'dh': 4.5 },
    'M5': {
        'd': 5,
        'P': 0.8,
        'd2': 4.48,
        'd3': 4.134,
        'As': 14.2,
        'dw': 10,
        'dh': 5.5 },
    'M6': {
        'd': 6,
        'P': 1,
        'd2': 5.35,
        'd3': 4.917,
        'As': 20.1,
        'dw': 12,
        'dh': 6.6 },
    'M8': {
        'd': 8,
        'P': 1.25,
        'd2': 7.188,
        'd3': 6.647,
        'As': 36.6,
        'dw': 16,
        'dh': 9 },
    'M10': {
        'd': 10,
        'P': 1.5,
        'd2': 9.026,
        'd3': 8.376,
        'As': 58,
        'dw': 20,
        'dh': 11 },
    'M12': {
        'd': 12,
        'P': 1.75,
        'd2': 10.863,
        'd3': 10.106,
        'As': 84.3,
        'dw': 24,
        'dh': 13.5 },
    'M14': {
        'd': 14,
        'P': 2,
        'd2': 12.701,
        'd3': 11.835,
        'As': 115,
        'dw': 28,
        'dh': 15.5 },
    'M16': {
        'd': 16,
        'P': 2,
        'd2': 14.701,
        'd3': 13.835,
        'As': 157,
        'dw': 30,
        'dh': 17.5 },
    'M18': {
        'd': 18,
        'P': 2.5,
        'd2': 16.376,
        'd3': 15.294,
        'As': 192,
        'dw': 34,
        'dh': 20 },
    'M20': {
        'd': 20,
        'P': 2.5,
        'd2': 18.376,
        'd3': 17.294,
        'As': 245,
        'dw': 36,
        'dh': 22 },
    'M22': {
        'd': 22,
        'P': 2.5,
        'd2': 20.376,
        'd3': 19.294,
        'As': 303,
        'dw': 40,
        'dh': 24 },
    'M24': {
        'd': 24,
        'P': 3,
        'd2': 22.051,
        'd3': 20.752,
        'As': 353,
        'dw': 44,
        'dh': 26 },
    'M27': {
        'd': 27,
        'P': 3,
        'd2': 25.051,
        'd3': 23.752,
        'As': 459,
        'dw': 50,
        'dh': 30 },
    'M30': {
        'd': 30,
        'P': 3.5,
        'd2': 27.727,
        'd3': 26.211,
        'As': 561,
        'dw': 56,
        'dh': 33 },
    'M36': {
        'd': 36,
        'P': 4,
        'd2': 33.402,
        'd3': 31.67,
        'As': 816,
        'dw': 66,
        'dh': 39 },
    'M42': {
        'd': 42,
        'P': 4.5,
        'd2': 39.077,
        'd3': 37.129,
        'As': 1120,
        'dw': 78,
        'dh': 45 },
    'M48': {
        'd': 48,
        'P': 5,
        'd2': 44.752,
        'd3': 42.587,
        'As': 1470,
        'dw': 88,
        'dh': 52 } }
@dataclass
class BoltJointResult:
    preload: float
    friction_force: float
    bolt_tension_capacity: float
    bolt_shear_capacity: float
    plate_bearing_capacity: float
    plate_tearout_capacity: float
    separation_load: float
    max_safe_load: float
    failure_mode: str
    safety_factor: float
    details: Dict = field(default_factory=dict)


@dataclass
class ScrewJointResult:
    preload: float
    thread_stripping_force: float
    screw_tension_capacity: float
    plate_bearing_capacity: float
    plate_tearout_capacity: float
    max_safe_load: float
    failure_mode: str
    safety_factor: float
    details: Dict = field(default_factory=dict)

def get_bolt_material(grade, diameter = (None,)):
    '''返回螺栓材料性能，d>16mm时8.8级强度降低'''
    m = BOLT_MATERIALS[grade]
    if grade == '8.8' and diameter is not None and diameter > 16:
        return {
            'name': m['name'],
            'sigma_u': 800,
            'sigma_s': 640,
            'HRC_max': m['HRC_max'] }
    return m


def calculate_preload(sigma_s = None, As = dataclass):
    return 0.7 * sigma_s * As


def calculate_bolt_stiffness(d = None, As = None, l_grip = None, E_bolt = (206000,)):
    L_eff = l_grip + 0.8 * d
    return E_bolt * As / L_eff


def calculate_bolt_length(d = None, l_grip = None):
    P_map = {
        3: 0.5,
        4: 0.7,
        5: 0.8,
        6: 1,
        8: 1.25,
        10: 1.5,
        12: 1.75,
        14: 2,
        16: 2,
        18: 2.5,
        20: 2.5,
        22: 2.5,
        24: 3,
        27: 3,
        30: 3.5,
        36: 4,
        42: 4.5,
        48: 5 }
    P = P_map.get(int(d), 2)
    H_nut = 0.8 * d
    A = 2 * P if l_grip + H_nut <= 50 else 3 * P
    L_calc = l_grip + H_nut + A
    std_lens = [
        20,
        25,
        30,
        35,
        40,
        45,
        50,
        55,
        60,
        65,
        70,
        75,
        80,
        90,
        100,
        110,
        120,
        130,
        140,
        150,
        160,
        180,
        200]
    L_std = std_lens[-1]
    for L in std_lens:
        if L >= L_calc:
            L_std = L
        
        return {
            'calc_length': L_calc,
            'standard_length': L_std,
            'l_grip': l_grip,
            'H_nut': H_nut,
            'A': A,
            'P': P }


def calculate_member_stiffness(d, dw, l_grip, E_plate, plate_thickness, n_plates = (2,)):
    E_bolt = 206000
    E_ratio = E_plate / E_bolt
    if E_ratio >= 0.95:
        base_ratio = 5
    elif E_ratio >= 0.55:
        base_ratio = 3.5
    elif E_ratio >= 0.45:
        base_ratio = 3
    elif E_ratio >= 0.3:
        base_ratio = 2.5
    else:
        base_ratio = 1.5
    lg_d_ratio = l_grip / d
    if lg_d_ratio > 4:
        length_factor = 1.2
    elif lg_d_ratio > 2:
        length_factor = 1
    else:
        length_factor = 0.8
    plate_factor = 1 / (1 + 0.15 * (n_plates - 1))
    stiffness_ratio = base_ratio * length_factor * plate_factor
    stiffness_ratio = max(1.5, min(8, stiffness_ratio))
    return stiffness_ratio


def calculate_load_factor(C_bolt, C_member):
    total = C_bolt + C_member
    return C_bolt / total if total > 0 else 0.5


def calculate_friction_force(preload, mu, n_bolts, n_surfaces = (1, 2)):
    return mu * preload * n_bolts * n_surfaces


def calculate_bolt_tension_capacity(sigma_s, As):
    return sigma_s * As


def calculate_bolt_shear_capacity(sigma_u, d, n_shear_planes = 1):
    '''
    螺栓抗剪承载力 Nv = nv × Ag × fvb
    Ag = π×d²/4 (毛截面积，非螺纹应力截面积)
    fvb = αv × fub (GB 50017-2017 表4.4.6)
    来源：GB 50017-2017 第11.4.1条 式11.4.1-1
    注：此处sigma_u即fub（螺栓极限抗拉强度）
    '''
    Ag = math.pi * d * d / 4
    if sigma_u <= 400:
        alpha_v = 0.35
    elif sigma_u <= 830:
        alpha_v = 0.38
    else:
        alpha_v = 0.385542
    fvb = alpha_v * sigma_u
    return fvb * Ag * n_shear_planes


def calculate_plate_bearing_capacity(sigma_u, d, t):
    return 2.4 * sigma_u * d * t


def calculate_plate_tearout_capacity(sigma_u, t, e1):
    tau_u = 0.6 * sigma_u
    return 2 * e1 * t * tau_u


def calculate_moment_forces(M, bolt_positions):
    if not bolt_positions:
        return []
    sum_r2 = sum(x ** 2 + y ** 2 for x, y in bolt_positions)
    if sum_r2 == 0:
        return [(0, 0)] * len(bolt_positions)
    forces = []
    for x, y in bolt_positions:
        fx_mom = M * y / sum_r2
        fy_mom = -M * x / sum_r2
        forces.append((fx_mom, fy_mom))
    return forces


def calculate_separation_safety(preload, phi, F_axial, F_K_req = None,
                                preload_min = None):
    F_M_min = preload_min if not preload_min is None else preload
    denominator = (1 - phi) * F_axial
    if denominator <= 0:
        return float('inf')
    return F_M_min / denominator


def _generate_warnings(d, bolt_positions, n_bolts, actual_min_edge, plate_thickness):
    '''生成布局和设计警告'''
    warns = []
    bolt_min_edge = 1.5 * d
    bolt_min_spacing = 3 * d
    d = d
    if actual_min_edge < bolt_min_edge:
        warns.append(f'''边距不足: {actual_min_edge:.1f}mm < {bolt_min_edge:.1f}mm(≥1.5d)''')
    if bolt_positions and n_bolts > 1:
        for i in range(len(bolt_positions)):
            for j in range(i + 1, len(bolt_positions)):
                (x1, y1) = bolt_positions[i]
                (x2, y2) = bolt_positions[j]
                dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                if dist < bolt_min_spacing:
                    warns.append(f'''螺栓间距不足: {dist:.1f}mm < {bolt_min_spacing:.1f}mm(≥3d)''')
                
                if plate_thickness < d * 0.5:
                    warns.append(f'''板厚偏薄: {plate_thickness:.1f}mm < {d * 0.5:.1f}mm(建议≥0.5d)''')
    return warns


def calculate_bolt_joint(bolt_size, bolt_grade, plate_material, plate_thickness, friction_surface, external_force_x, external_force_y, force_eccentricity, n_bolts, n_surfaces, edge_distance, bolt_positions, custom_mu = None):
    bolt = BOLT_SIZES[bolt_size]
    grade = get_bolt_material(bolt_grade, bolt['d'])
    plate = PLATE_MATERIALS[plate_material]
    if not custom_mu is None:
        mu = custom_mu
    else:
        mu_entry = FRICTION_COEFFICIENTS.get(friction_surface, { })
        mu = mu_entry.get('mu', 0.3) if isinstance(mu_entry, dict) else float(mu_entry)
    d = bolt['d']
    As = bolt['As']
    dw = bolt['dw']
    dh = bolt['dh']
    sigma_s_bolt = grade['sigma_s']
    sigma_u_bolt = grade['sigma_u']
    sigma_u_plate = plate['sigma_u']
    E_plate = plate['E']
    if edge_distance is None:
        edge_distance = 1.5 * d
    actual_min_edge = edge_distance
    if bolt_positions and len(bolt_positions) > 1:
        min_dist_to_center = min(math.sqrt(x ** 2 + y ** 2)
                                 for x, y in bolt_positions)
        actual_edge = min_dist_to_center - d / 2
        if actual_edge > 0:
            actual_min_edge = max(edge_distance, actual_edge)
    preload = calculate_preload(sigma_s_bolt, As)
    alpha_A = 1.3
    preload_vdi_max = 0.9 * sigma_s_bolt * As
    preload_vdi_min = preload_vdi_max / alpha_A
    l_grip = 2 * plate_thickness
    bolt_len_info = calculate_bolt_length(d, l_grip)
    C_bolt = calculate_bolt_stiffness(d, As, l_grip, 206000)
    stiffness_ratio = calculate_member_stiffness(d, dw, l_grip, E_plate, plate_thickness, n_plates = 2)
    C_member = C_bolt * stiffness_ratio
    phi = calculate_load_factor(C_bolt, C_member)
    F_axial = external_force_y
    F_shear = external_force_x
    M = force_eccentricity
    if n_bolts == 1:
        bolt_moment_force_y = 0
        bolt_moment_force_x = 0
    elif bolt_positions is not None and len(bolt_positions) == n_bolts:
        positions = bolt_positions
    else:
        spacing = max(3 * d, 30)
        positions = [(spacing * math.cos(2 * math.pi * i / n_bolts),
                      spacing * math.sin(2 * math.pi * i / n_bolts))
                     for i in range(n_bolts)]
    mom_forces = calculate_moment_forces(M, positions)
    max_mom_force = max(mom_forces, key = (lambda f: math.sqrt(f[0] ** 2 + f[1] ** 2)))
    bolt_moment_force_y = max_mom_force[1]
    bolt_moment_force_x = max_mom_force[0]
    F_axial_total = F_axial / n_bolts + bolt_moment_force_y
    F_shear_total = F_shear / n_bolts + bolt_moment_force_x
    F_total = math.sqrt(F_axial_total ** 2 + F_shear_total ** 2)
    friction_force = calculate_friction_force(preload, mu, n_bolts, n_surfaces)
    bolt_tension_cap = calculate_bolt_tension_capacity(sigma_s_bolt, As)
    bolt_shear_cap = calculate_bolt_shear_capacity(sigma_u_bolt, d)
    plate_bearing_cap = calculate_plate_bearing_capacity(sigma_u_plate, d, plate_thickness)
    plate_tearout_cap = calculate_plate_tearout_capacity(sigma_u_plate, plate_thickness, actual_min_edge)
    separation_load = preload / (1 - phi) if phi < 1 else preload
    safety_factors = { }
    safety_factors['friction'] = friction_force / abs(F_shear) if F_shear != 0 else float('inf')
    F_bolt_total = preload + phi * F_axial_total
    safety_factors['bolt_yield'] = bolt_tension_cap / F_bolt_total if F_bolt_total > 0 else float('inf')
    safety_factors['separation'] = calculate_separation_safety(preload, phi, F_axial_total, preload_min = preload_vdi_min)
    safety_factors['bolt_shear'] = bolt_shear_cap / abs(F_shear_total) if F_shear_total != 0 else float('inf')
    safety_factors['plate_bearing'] = plate_bearing_cap / abs(F_shear_total) if F_shear_total != 0 else float('inf')
    safety_factors['plate_tearout'] = plate_tearout_cap / abs(F_shear_total) if F_shear_total != 0 else float('inf')
    min_sf = min(safety_factors.values())
    failure_mode = min(safety_factors, key = safety_factors.get)
    max_loads = { }
    max_loads['friction'] = friction_force
    if phi > 0:
        max_axial_total = (bolt_tension_cap - preload) / phi
        max_axial_ext = (max_axial_total - bolt_moment_force_y) * n_bolts
        max_loads['bolt_yield'] = max(0, max_axial_ext)
    if phi < 1 and phi > 0:
        max_sep_axial_total = preload_vdi_min / (1 - phi)
        max_sep_axial_ext = (max_sep_axial_total - bolt_moment_force_y) * n_bolts
        max_loads['separation'] = max(0, max_sep_axial_ext)
    for mode in ('bolt_shear', 'plate_bearing', 'plate_tearout'):
        caps = {
            'bolt_shear': bolt_shear_cap,
            'plate_bearing': plate_bearing_cap,
            'plate_tearout': plate_tearout_cap }
        cap = caps[mode]
        sf_val = safety_factors[mode]
        if sf_val > 0 and sf_val < float('inf'):
            max_shear_ext = (cap - bolt_moment_force_x) * n_bolts
            max_loads[mode] = max(0, max_shear_ext)
    details = {
        'bolt_size': bolt_size,
        'bolt_grade': bolt_grade,
        'plate_material': plate_material,
        'd': d,
        'As': As,
        'dw': dw,
        'dh': dh,
        'sigma_s_bolt': sigma_s_bolt,
        'sigma_u_bolt': sigma_u_bolt,
        'sigma_u_plate': sigma_u_plate,
        'mu': mu,
        'E_plate': E_plate,
        'preload': preload,
        'preload_vdi_max': preload_vdi_max,
        'preload_vdi_min': preload_vdi_min,
        'alpha_A': alpha_A,
        'C_bolt': C_bolt,
        'C_member': C_member,
        'phi': phi,
        'friction_force': friction_force,
        'bolt_tension_cap': bolt_tension_cap,
        'bolt_shear_cap': bolt_shear_cap,
        'plate_bearing_cap': plate_bearing_cap,
        'plate_tearout_cap': plate_tearout_cap,
        'separation_load': separation_load,
        'F_axial': F_axial_total,
        'F_shear': F_shear_total,
        'F_total': F_total,
        'F_bolt_total': F_bolt_total,
        '_M_external': force_eccentricity,
        '_actual_min_edge': actual_min_edge,
        '_n_surfaces': n_surfaces,
        '_bolt_length': bolt_len_info,
        'safety_factors': safety_factors,
        'warnings': _generate_warnings(d, bolt_positions, n_bolts, actual_min_edge, plate_thickness) }
    max_safe_load = min(max_loads.values()) if max_loads else 0.0
    return BoltJointResult(preload = preload, friction_force = friction_force, bolt_tension_capacity = bolt_tension_cap, bolt_shear_capacity = bolt_shear_cap, plate_bearing_capacity = plate_bearing_cap, plate_tearout_capacity = plate_tearout_cap, separation_load = separation_load, max_safe_load = max_safe_load, failure_mode = failure_mode, safety_factor = min_sf, details = details)


def calculate_screw_thread_stripping_force(d, p, n_threads, sigma_u_plate):
    tau = 0.6 * sigma_u_plate
    A_thread = math.pi * d * p * n_threads
    return tau * A_thread


def _generate_screw_warnings(d, edge_distance, engagement_length, plate_thickness):
    '''生成螺钉连接警告'''
    warns = []
    min_edge = 1.5 * d
    if edge_distance < min_edge:
        warns.append(f'''边距不足: {edge_distance:.1f}mm < {min_edge:.1f}mm(≥1.5d)''')
    min_eng = 1 * d
    if engagement_length < min_eng:
        warns.append(f'''旋入深度不足: {engagement_length:.1f}mm < {min_eng:.1f}mm(≥1d)''')
    if plate_thickness < d * 0.5:
        warns.append(f'''板厚偏薄: {plate_thickness:.1f}mm < {d * 0.5:.1f}mm(建议≥0.5d)''')
    return warns


def calculate_screw_joint(screw_size, screw_grade, plate_material, plate_thickness, external_force_x, external_force_y, force_eccentricity, n_screws, edge_distance, engagement_depth_mm, thread_engagement_ratio = None):
    bolt = BOLT_SIZES[screw_size]
    grade = get_bolt_material(screw_grade, bolt['d'])
    plate = PLATE_MATERIALS[plate_material]
    d = bolt['d']
    P = bolt['P']
    As = bolt['As']
    dw = bolt['dw']
    sigma_s_screw = grade['sigma_s']
    sigma_u_screw = grade['sigma_u']
    sigma_u_plate = plate['sigma_u']
    if edge_distance is None:
        edge_distance = 1.5 * d
    _MAT_ENGAGEMENT_DEFAULTS = {
        'Q235': 1,
        'Q345': 1,
        'Q460': 1,
        '20#': 1,
        '45#': 1,
        '40Cr': 1,
        '20CrMnTi': 1,
        'HT200': 1.25,
        'HT250': 1.25,
        'QT450-10': 1.25,
        '304': 1,
        '316': 1,
        '5052': 2,
        '6061-T6': 2,
        '6063-T5': 2,
        '7075-T6': 2,
        'TC4': 1.5,
        **{
            'PA66': 2.5,
            'PEEK': 2.5 } }
    if engagement_depth_mm is not None:
        engagement_length = engagement_depth_mm
        engagement_ratio_used = engagement_length / d
    elif thread_engagement_ratio is not None:
        engagement_length = thread_engagement_ratio * d
        engagement_ratio_used = thread_engagement_ratio
    else:
        engagement_ratio_used = _MAT_ENGAGEMENT_DEFAULTS.get(plate_material, 1.5)
        engagement_length = engagement_ratio_used * d
    n_threads = max(1, int(engagement_length / P))
    preload = calculate_preload(sigma_s_screw, As)
    thread_stripping_force = calculate_screw_thread_stripping_force(d, P, n_threads, sigma_u_plate)
    screw_tension_cap = calculate_bolt_tension_capacity(sigma_s_screw, As)
    plate_bearing_cap = calculate_plate_bearing_capacity(sigma_u_plate, d, plate_thickness)
    plate_tearout_cap = calculate_plate_tearout_capacity(sigma_u_plate, plate_thickness, edge_distance)
    F_axial = external_force_y / n_screws
    F_shear = external_force_x / n_screws
    F_total = math.sqrt(F_axial ** 2 + F_shear ** 2)
    safety_factors = { }
    F_screw_total = preload + F_axial
    safety_factors['screw_yield'] = screw_tension_cap / F_screw_total if F_screw_total > 0 else float('inf')
    safety_factors['thread_stripping'] = thread_stripping_force / F_axial if F_axial > 0 else float('inf')
    safety_factors['plate_bearing'] = plate_bearing_cap / abs(F_shear) if F_shear != 0 else float('inf')
    safety_factors['plate_tearout'] = plate_tearout_cap / abs(F_shear) if F_shear != 0 else float('inf')
    min_sf = min(safety_factors.values())
    failure_mode = min(safety_factors, key = safety_factors.get)
    max_loads = { }
    max_loads['thread_stripping'] = thread_stripping_force
    max_axial_screw = screw_tension_cap - preload
    max_loads['screw_yield'] = max(0, max_axial_screw)
    for mode in ('plate_bearing', 'plate_tearout'):
        caps = {
            'plate_bearing': plate_bearing_cap,
            'plate_tearout': plate_tearout_cap }
        cap = caps[mode]
        sf_val = safety_factors[mode]
        if sf_val > 0 and sf_val < float('inf'):
            max_loads[mode] = cap
        if max_loads:
            max_safe_load = min(max_loads.values())
        else:
            max_safe_load = 2 * preload
    details = {
        'screw_size': screw_size,
        'screw_grade': screw_grade,
        'plate_material': plate_material,
        'd': d,
        'P': P,
        'As': As,
        'dw': dw,
        'sigma_s_screw': sigma_s_screw,
        'sigma_u_screw': sigma_u_screw,
        'sigma_u_plate': sigma_u_plate,
        'engagement_length': engagement_length,
        'engagement_ratio': engagement_ratio_used,
        'n_threads': n_threads,
        'preload': preload,
        'thread_stripping_force': thread_stripping_force,
        'screw_tension_cap': screw_tension_cap,
        'plate_bearing_cap': plate_bearing_cap,
        **{
            'plate_tearout_cap': plate_tearout_cap,
            'F_axial': F_axial,
            'F_shear': F_shear,
            'F_total': F_total,
            'F_screw_total': F_screw_total,
            'safety_factors': safety_factors,
            'warnings': _generate_screw_warnings(d, edge_distance, engagement_length, plate_thickness) } }
    return ScrewJointResult(preload = preload, thread_stripping_force = thread_stripping_force, screw_tension_capacity = screw_tension_cap, plate_bearing_capacity = plate_bearing_cap, plate_tearout_capacity = plate_tearout_cap, max_safe_load = max_safe_load, failure_mode = failure_mode, safety_factor = min_sf, details = details)

