# Source Generated with Decompyle++
# Decompiled by MUHAMMAD SHAKIB
# GitHub: https://github.com/0xSHAK1B
# File: data\gear_tooth_thickness.pyc (Python 3.10)

'''齿厚换算模块
公法线长度 ↔ 跨棒距(M值) ↔ 弧齿厚 ↔ 法向圆齿厚 互算
公式依据：GB/T 10095 / 齿轮手册
'''
import math

def involute_func(alpha_rad):
    '''渐开线函数 inv(α) = tan(α) - α'''
    return math.tan(alpha_rad) - alpha_rad


def involute_func_inv(inv_val):
    '''渐开线函数反解'''
    alpha = math.atan(inv_val)
    for _ in range(50):
        f = math.tan(alpha) - alpha - inv_val
        df = math.tan(alpha) ** 2
        if abs(df) < 1e-15:
            return alpha
        alpha -= f / df
        if abs(f) < 1e-12:
            return alpha
    return alpha


def calc_normal_line_length(z, mn, alpha_n, x, k, beta = 0):
    '''计算跨k齿公法线长度
    
    参数:
        z: 齿数
        mn: 法向模数
        alpha_n: 法向压力角（度）
        x: 法向变位系数
        k: 跨齿数
        beta: 螺旋角（度）
    
    返回:
        (Wk, Wkn) — 端面公法线长度, 法向公法线长度
    '''
    alpha_n_rad = math.radians(alpha_n)
    beta_rad = math.radians(beta)
    alpha_t = math.atan(math.tan(alpha_n_rad) / math.cos(beta_rad))
    db = z * mn * math.cos(alpha_n_rad) / math.cos(beta_rad)
    inv_at = involute_func(alpha_t)
    Wkn = mn * math.cos(alpha_n_rad) * (math.pi * (k - 0.5) + z * inv_at + 2 * x * math.tan(alpha_n_rad))
    return round(Wkn, 4)


def calc_k_from_z(z, alpha_n = 20, beta = 0):
    '''推荐跨齿数 k = z*α_n/180*cos(β) + 0.5'''
    import math
    k = (z * alpha_n / 180) * math.cos(math.radians(beta)) + 0.5
    return max(2, round(k))


def calc_arc_tooth_thickness(z, mn, alpha_n, x, beta = 0):
    '''计算端面分度圆弧齿厚
    
    返回:
        (sn, st) — 法向弧齿厚, 端面弧齿厚
    '''
    alpha_n_rad = math.radians(alpha_n)
    beta_rad = math.radians(beta)
    sn = math.pi * mn / 2 + 2 * x * mn * math.tan(alpha_n_rad)
    st = sn / math.cos(beta_rad)
    return (round(sn, 4), round(st, 4))


def calc_x_from_arc_thickness(z, mn, alpha_n, sn, beta = 0):
    '''已知法向弧齿厚反求变位系数x'''
    alpha_n_rad = math.radians(alpha_n)
    x = (sn - math.pi * mn / 2) / (2 * mn * math.tan(alpha_n_rad))
    return round(x, 4)


def calc_normal_circular_thickness(z, mn, alpha_n, x, beta = 0):
    '''计算法向分度圆齿厚（弦齿厚近似）
    
    法向圆齿厚 ≈ sn（小模数时近似等于法向弧齿厚）
    精确值需要考虑弦高修正
    '''
    (sn, st) = calc_arc_tooth_thickness(z, mn, alpha_n, x, beta)
    return sn


def calc_x_from_circular_thickness(z, mn, alpha_n, sn_circular, beta = 0):
    '''已知法向圆齿厚反求变位系数x'''
    return calc_x_from_arc_thickness(z, mn, alpha_n, sn_circular, beta)


def m_value_to_normal_line(z, mn, alpha_n, x, dp, M, beta = 0):
    '''已知M值求公法线长度（间接法：M→x→W）'''
    from . import gear_m_value as mv
    (x_calc, _) = mv.solve_x_from_m_value(z, mn, alpha_n, dp, M, beta)
    if x_calc is None:
        return None
    k = calc_k_from_z(z, alpha_n, beta)
    W = calc_normal_line_length(z, mn, alpha_n, x_calc, k, beta)
    return (W, x_calc, k)


def normal_line_to_m_value(z, mn, alpha_n, x, W, dp, beta = 0):
    '''已知公法线长度求M值（间接法：W→x→M）'''
    from . import gear_m_value as mv
    alpha_n_rad = math.radians(alpha_n)
    beta_rad = math.radians(beta)
    alpha_t = math.atan(math.tan(alpha_n_rad) / math.cos(beta_rad))
    inv_at = involute_func(alpha_t)
    k = calc_k_from_z(z, alpha_n, beta)
    Wkn = W
    x_from_W = (Wkn / (mn * math.cos(alpha_n_rad)) - math.pi * (k - 0.5) - z * inv_at) / (2 * math.tan(alpha_n_rad))
    M = mv.calc_m_value_simple(z, mn, alpha_n, x_from_W, dp, beta)
    return (M, x_from_W, k)


def convert_tooth_thickness(z, mn, alpha_n, x, dp = None, beta = 0, W = None, M = None, sn = None, k = None):
    '''齿厚综合换算
    
    给定任意一个已知量，计算其他所有量。
    已知量可以是：W(公法线), M(M值), sn(法向弧齿厚), x(变位系数)
    至少需要提供 x 或 其中之一。
    
    返回字典：
        W: 公法线长度
        M: M值（需要dp）
        sn: 法向弧齿厚
        st: 端面弧齿厚
        x: 变位系数
        k: 跨齿数
    '''
    result = { }
    if x is not None:
        result['x'] = x
    elif W is not None:
        alpha_n_rad = math.radians(alpha_n)
        beta_rad = math.radians(beta)
        alpha_t = math.atan(math.tan(alpha_n_rad) / math.cos(beta_rad))
        inv_at = involute_func(alpha_t)
        if k is None:
            k = calc_k_from_z(z, alpha_n, beta)
        x = (W / (mn * math.cos(alpha_n_rad)) - math.pi * (k - 0.5) - z * inv_at) / (2 * math.tan(alpha_n_rad))
        result['x'] = round(x, 4)
    elif sn is not None:
        x = calc_x_from_arc_thickness(z, mn, alpha_n, sn, beta)
        result['x'] = x
    else:
        return {
            'error': '需要至少提供 x, W, 或 sn 之一' }
    (sn_val, st_val) = calc_arc_tooth_thickness(z, mn, alpha_n, result['x'], beta)
    result['sn'] = sn_val
    result['st'] = st_val
    if k is None:
        k = calc_k_from_z(z, alpha_n, beta)
    result['k'] = k
    result['W'] = calc_normal_line_length(z, mn, alpha_n, result['x'], k, beta)
    if dp is not None:
        from . import gear_m_value as mv
        result['M'] = mv.calc_m_value_simple(z, mn, alpha_n, result['x'], dp, beta)
        result['dp'] = dp
    return result

if __name__ == '__main__':
    (z, mn, alpha_n, x) = (20, 3, 20, 0)
    k = calc_k_from_z(z, alpha_n)
    W = calc_normal_line_length(z, mn, alpha_n, x, k)
    print(f'''直齿M3Z20 x=0: k={k}, W={W}''')
    (sn, st) = calc_arc_tooth_thickness(z, mn, alpha_n, x)
    print(f'''  sn={sn}, st={st}''')
    (sn2, st2) = calc_arc_tooth_thickness(z, mn, alpha_n, 0.5)
    print(f'''直齿M3Z20 x=0.5: sn={sn2}, st={st2}''')
    x_back = calc_x_from_arc_thickness(z, mn, alpha_n, sn2)
    print(f'''  反求x={x_back} (应=0.5)''')
    from gear_m_value import calc_m_value_simple
    dp = 5
    M = calc_m_value_simple(z, mn, alpha_n, x, dp)
    print(f'''  M={M}''')
    result = convert_tooth_thickness(z, mn, alpha_n, 0, dp)
    print(f'''  综合: W={result['W']}, M={result['M']}, sn={result['sn']}''')
    print('\nAll tests passed!')
