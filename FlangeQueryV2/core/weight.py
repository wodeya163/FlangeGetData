# -*- coding: utf-8 -*-
"""管件重量计算（纯函数，单位：mm / m / kg）。"""

import math

DENSITY_STEEL = 7850.0

# 大曲率弯头常用材质（密度 kg/m³）
ELBOW_MATERIALS = {
    '碳钢 20#': 7850.0,
    '不锈钢 304': 7930.0,
    '不锈钢 316L': 7980.0,
    '合金钢 15CrMo': 7850.0,
    '低温钢 09MnNiDR': 7850.0,
    '铝 6061': 2700.0,
    '铜 T2': 8960.0,
    'PP 塑料': 910.0,
}


def _check_positive(**values):
    for key, value in values.items():
        if value <= 0:
            raise ValueError('%s 必须大于 0' % key)


def _area(od, wall):
    """圆环截面积 mm²。"""
    return math.pi * (od - wall) * wall


def _volume_m3(area_mm2, length_mm):
    return area_mm2 * length_mm / 1_000_000_000.0


def pipe_weight(od, wall, length_m, density=DENSITY_STEEL):
    """直管重量。od/wall: mm，length_m: m，density: kg/m³。"""
    _check_positive(od=od, wall=wall, length_m=length_m, density=density)
    if wall * 2 >= od:
        raise ValueError('壁厚必须小于外径的一半')
    area = _area(od, wall)
    volume = _volume_m3(area, length_m * 1000.0)
    mass = volume * density
    return {
        'mass': mass,
        'volume': volume,
        'area': area,
        'formula': 'm = ρ × π × (D − S) × S × L',
        'detail': '截面积 %.2f mm²，体积 %.6f m³' % (area, volume),
    }


def elbow_weight(od, wall, radius, angle, density=DENSITY_STEEL):
    """弯头重量。radius: 弯曲半径 mm，angle: 度。"""
    _check_positive(od=od, wall=wall, radius=radius, angle=angle,
                    density=density)
    if wall * 2 >= od:
        raise ValueError('壁厚必须小于外径的一半')
    theta = math.radians(angle)
    area = _area(od, wall)
    length = radius * theta
    volume = _volume_m3(area, length)
    mass = volume * density
    return {
        'mass': mass,
        'volume': volume,
        'area': area,
        'formula': 'm = ρ × π × (D − S) × S × R × θ',
        'detail': '中心线长 %.1f mm，截面积 %.2f mm²' % (length, area),
    }


def large_radius_elbow_weight(od, wall, radius, angle, tangent1=0.0,
                              tangent2=0.0, density=DENSITY_STEEL):
    """大曲率弯头：中心线弧长 + 两端直段。单位 mm / 度 / kg/m³。"""
    _check_positive(od=od, wall=wall, radius=radius, angle=angle,
                    density=density)
    if wall * 2 >= od:
        raise ValueError('壁厚必须小于外径的一半')
    tangent1 = max(0.0, tangent1)
    tangent2 = max(0.0, tangent2)
    theta = math.radians(angle)
    area = _area(od, wall)
    arc_length = radius * theta
    length = arc_length + tangent1 + tangent2
    volume = _volume_m3(area, length)
    mass = volume * density
    return {
        'mass': mass,
        'volume': volume,
        'area': area,
        'arc_length': arc_length,
        'tangent_length': tangent1 + tangent2,
        'formula': 'm = ρ × π × (D − S) × S × (Rθ + L1 + L2)',
        'detail': '弧长 %.1f mm，直段 %.1f mm，总中心线长 %.1f mm'
                  % (arc_length, tangent1 + tangent2, length),
    }


def tee_weight(od_main, od_branch, wall, main_length, branch_length,
               density=DENSITY_STEEL, price_per_kg=0.0):
    """三通重量近似：主管 + 支管两段圆环体积。"""
    _check_positive(od_main=od_main, od_branch=od_branch, wall=wall,
                    main_length=main_length, branch_length=branch_length,
                    density=density)
    if wall * 2 >= min(od_main, od_branch):
        raise ValueError('壁厚必须小于外径的一半')
    area_main = _area(od_main, wall)
    area_branch = _area(od_branch, wall)
    volume = (_volume_m3(area_main, main_length) +
              _volume_m3(area_branch, branch_length))
    mass = volume * density
    return {
        'mass': mass,
        'volume': volume,
        'area': area_main + area_branch,
        'formula': 'm = ρ × [A主 × L主 + A支 × L支]',
        'detail': '主管截面积 %.2f mm²，支管截面积 %.2f mm²'
                  % (area_main, area_branch),
        'price': mass * price_per_kg if price_per_kg > 0 else None,
    }


def angle_tee_weight(od_main, od_branch, wall, main_length, branch_height,
                     angle, density=DENSITY_STEEL, price_per_kg=0.0):
    """斜三通：支管按与主管夹角斜接，branch_height 为垂直高度。"""
    _check_positive(od_main=od_main, od_branch=od_branch, wall=wall,
                    main_length=main_length, branch_height=branch_height,
                    angle=angle, density=density)
    if not 0 < angle < 180:
        raise ValueError('支管夹角需在 0~180° 之间')
    if wall * 2 >= min(od_main, od_branch):
        raise ValueError('壁厚必须小于外径的一半')
    area_main = _area(od_main, wall)
    area_branch = _area(od_branch, wall)
    branch_length = branch_height / math.sin(math.radians(angle))
    volume = (_volume_m3(area_main, main_length) +
              _volume_m3(area_branch, branch_length))
    mass = volume * density
    return {
        'mass': mass, 'volume': volume, 'area': area_main + area_branch,
        'branch_length': branch_length,
        'formula': 'm = ρ × [A主 × L主 + A支 × (H支 / sinθ)]',
        'detail': '支管斜长 %.1f mm（高度 %.1f mm，夹角 %.0f°）'
                  % (branch_length, branch_height, angle),
        'price': mass * price_per_kg if price_per_kg > 0 else None,
    }


def bend_tee_weight(od_main, od_branch, wall, main_length, branch_length,
                    bend_radius, bend_angle, density=DENSITY_STEEL,
                    price_per_kg=0.0):
    """弯三通：主管 + 支管直段 + 支管弯头弧段。"""
    _check_positive(od_main=od_main, od_branch=od_branch, wall=wall,
                    main_length=main_length, branch_length=branch_length,
                    bend_radius=bend_radius, bend_angle=bend_angle,
                    density=density)
    if wall * 2 >= min(od_main, od_branch):
        raise ValueError('壁厚必须小于外径的一半')
    area_main = _area(od_main, wall)
    area_branch = _area(od_branch, wall)
    arc = bend_radius * math.radians(bend_angle)
    branch_total = branch_length + arc
    volume = (_volume_m3(area_main, main_length) +
              _volume_m3(area_branch, branch_total))
    mass = volume * density
    return {
        'mass': mass, 'volume': volume, 'area': area_main + area_branch,
        'branch_length': branch_total,
        'formula': 'm = ρ × [A主 × L主 + A支 × (L直 + Rθ)]',
        'detail': '支管直段 %.1f mm，弯弧 %.1f mm，支管总长 %.1f mm'
                  % (branch_length, arc, branch_total),
        'price': mass * price_per_kg if price_per_kg > 0 else None,
    }
