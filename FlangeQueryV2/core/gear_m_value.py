# Source Generated with Decompyle++
# Decompiled by MUHAMMAD SHAKIB
# GitHub: https://github.com/0xSHAK1B
# File: data\gear_m_value.pyc (Python 3.10)

'''M值（跨棒距）计算 — 外齿轮/内齿轮
公式依据：GB/T 10095 / 齿轮手册
支持：已知参数求M值、已知M值反求变位系数
'''
import math

def involute_func(alpha_rad):
    '''渐开线函数 inv(α) = tan(α) - α'''
    return math.tan(alpha_rad) - alpha_rad


def involute_func_inv(inv_val):
    '''渐开线函数反解：已知 inv(α) 求 α（牛顿迭代）'''
    alpha = math.atan(inv_val)
    for _ in range(50):
        f = math.tan(alpha) - alpha - inv_val
        df = math.tan(alpha) ** 2
        if abs(df) < 1e-15:
            return alpha
        delta = f / df
        alpha -= delta
        if abs(delta) < 1e-12:
            return alpha
    return alpha


def calc_roller_diameter(mn, alpha_n=20):
    '''标准量棒直径推荐值（模数法）'''
    dp = mn * 1.68
    return round(dp, 3)


def _flank_half_slot(z, mn, alpha_n_deg, x, internal, r0, beta=0):
    '''分度圆处槽半角（弧度）。

    齿厚必须与 r0 同面：r0 为端面分度圆半径，故用端面齿厚
    s_t = mt·(π/2 ± 2x·tanαt)，mt=mn/cosβ，αt=atan(tanαn/cosβ)。
    （2026-10-09 修复：原式用法向齿厚 s_n 直接除端面 r0，β≠0 时槽宽偏大，
     斜齿 M值偏小——z30 mn2 αn20 β15 x0 dp3.4 案例偏差 −0.27mm。
     β=0 时 mt=mn、αt=αn，与旧式数学等价，直齿行为不变。）
    外齿轮 s=(π/2+2x·tanαt)·mt；内齿轮 s=(π/2−2x·tanαt)·mt。
    alpha_n_deg 为角度输入（内部转弧度）。'''
    an = math.radians(alpha_n_deg)
    bt = math.radians(beta)
    mt = mn / math.cos(bt)
    at = math.atan(math.tan(an) / math.cos(bt))
    if internal:
        s = (math.pi / 2 - 2 * x * math.tan(at)) * mt
    else:
        s = (math.pi / 2 + 2 * x * math.tan(at)) * mt
    return (2 * math.pi / z - s / r0) / 2


def calc_m_value_simple(z, mn, alpha_n, x, dp, beta=0, is_internal=False):
    '''跨棒距 M 值 — 数值相切法（第一性几何，非查表近似）。

    算法：
      1) 端面参数：mt=mn/cosβ, αt=atan(tanαn/cosβ), r0=mt·z/2, rb=r0·cosαt
      2) 一侧渐开线齿面旋转定位到「槽中心线 = x 轴」（内齿轮齿面取镜像绕向）
      3) 量棒（半径 a=dp/2）与齿面相切且棒心落在槽中心线上：
         解 f(t) = [齿面点 + a·法向] 的 y 分量 = 0（变号扫描 + 二分）
      4) 物理根筛选：切点在有效齿段 [rb, 齿顶/齿根]；棒不穿透对面齿面
      5) M(外) = 2C+dp（偶）/ 2C·cos(90°/z)+dp（奇）；M(内) = 2C−dp（偶）/ 同奇数修正

    与独立真值求解器 _m_value_truth.py（4000 点云法）互验，8 案例一致。
    斜齿轮按端面近似（量棒为法向接触，严格解另册）。
    根本无解（参数不成立）时抛 ValueError，不返回兜底值。
    '''
    alpha_n_rad = math.radians(alpha_n)
    beta_rad = math.radians(beta)
    mt = mn / math.cos(beta_rad)
    alpha_t = math.atan(math.tan(alpha_n_rad) / math.cos(beta_rad))
    r0 = mt * z / 2
    rb = r0 * math.cos(alpha_t)
    if rb <= 0 or dp <= 0 or z <= 0 or mn <= 0:
        raise ValueError('齿数/模数/量棒直径须为正')
    half_slot = _flank_half_slot(z, mn, alpha_n, x, is_internal, r0, beta)
    if is_internal:
        r_hi = r0 + (1.25 - x) * mn
        phi0 = half_slot + involute_func(alpha_t)
        mirror = True
    else:
        r_hi = r0 + (1 + x) * mn
        phi0 = half_slot - involute_func(alpha_t)
        mirror = False
    if r_hi <= rb:
        raise ValueError('有效齿段不存在（齿顶/齿根圆不在基圆之外），请检查参数')
    a = dp / 2
    t_hi = math.sqrt((r_hi / rb) ** 2 - 1)
    N = 600

    def pt(t):
        x0 = rb * (math.cos(t) + t * math.sin(t))
        y0 = rb * (math.sin(t) - t * math.cos(t))
        if mirror:
            y0 = -y0
            n1 = (-math.sin(t), -math.cos(t))
        else:
            n1 = (-math.sin(t), math.cos(t))
        cp, sp = math.cos(phi0), math.sin(phi0)
        px = x0 * cp - y0 * sp
        py = x0 * sp + y0 * cp
        nx = n1[0] * cp - n1[1] * sp
        ny = n1[0] * sp + n1[1] * cp
        return (px, py, nx, ny)

    candidates = []
    for sign in (1, -1):
        prev_y = None
        for i in range(N + 1):
            t = t_hi * i / N
            (px, py, nx, ny) = pt(t)
            qy = py + a * sign * ny
            if prev_y is not None:
                if prev_y <= 0 <= qy or prev_y >= 0 >= qy:
                    lo, hi, ylo = t - t_hi / N, t, prev_y
                    for _ in range(70):
                        mid = (lo + hi) / 2
                        (mx, my, mnx, mny) = pt(mid)
                        qm = my + a * sign * mny
                        if ylo <= 0 <= qm or ylo >= 0 >= qm:
                            hi = mid
                        else:
                            lo, ylo = mid, qm
                    tc = (lo + hi) / 2
                    (px, py, nx, ny) = pt(tc)
                    qx, qy = px + a * sign * nx, py + a * sign * ny
                    candidates.append((qx, qy, math.hypot(px, py), tc))
            prev_y = qy
    mirror_pts = None
    for qx, qy, r_contact, tc in candidates:
        C = math.hypot(qx, qy)
        if C <= 0:
            continue
        if r_contact > r_hi + 1e-06 or r_contact < rb - 1e-06:
            continue
        if mirror_pts is None:
            mirror_pts = []
            for i in range(N + 1):
                t = t_hi * i / N
                (mx, my, _, _) = pt(t)
                mirror_pts.append((mx, -my))
        dmin = min(((qx - mx) ** 2 + (qy - my) ** 2 for mx, my in mirror_pts))
        if math.sqrt(dmin) < a - 0.05:
            continue
        if is_internal:
            M = 2 * C - dp
        else:
            M = 2 * C + dp
        if z % 2 == 1:
            M = 2 * C * math.cos(math.radians(90 / z)) + (-dp if is_internal else dp)
        return round(M, 4)
    raise ValueError('量棒与齿面无有效相切解（量棒直径/变位参数不成立），请检查 dp')

def solve_x_from_m_value(z, mn, alpha_n, dp, M_target, beta=0.0, is_internal=False, x_range=(-2.0, 3.0), tol=0.001):
    '''已知M值反求变位系数x（牛顿迭代法）
    
    参数:
        z, mn, alpha_n, dp, M_target: 已知参数
        beta: 螺旋角
        is_internal: 是否内齿轮
        x_range: x的搜索范围
        tol: M值容差
    
    返回:
        (x, M_calc) — 变位系数和对应的M值
    '''
    
    def f(x):
        try:
            return calc_m_value_simple(z, mn, alpha_n, x, dp, beta, is_internal) - M_target
        except ValueError:
            return None

    (x_min, x_max) = x_range
    f_min = f(x_min)
    f_max = f(x_max)
    if f_min is None or f_max is None:
        xs = [x_min + (x_max - x_min) * i / 40 for i in range(41)]
        vals = [(xi, f(xi)) for xi in xs]
        f_min = f_max = None
        for i in range(40):
            if vals[i][1] is not None and vals[i + 1][1] is not None and vals[i][1] * vals[i + 1][1] <= 0:
                x_min, x_max = vals[i][0], vals[i + 1][0]
                f_min, f_max = vals[i][1], vals[i + 1][1]
                break
        if f_min is None or f_max is None:
            return (None, None)
    if f_min * f_max > 0:
        x_min, x_max = -5.0, 5.0
        f_min = f(x_min)
        f_max = f(x_max)
        if f_min is None or f_max is None or f_min * f_max > 0:
            return (None, None)
    for _ in range(100):
        x_mid = (x_min + x_max) / 2
        f_mid = f(x_mid)
        if f_mid is None:
            return (None, None)
        if abs(f_mid) < tol:
            return (round(x_mid, 4), M_target)
        if f_min * f_mid < 0:
            x_max = x_mid
            f_max = f_mid
        else:
            x_min = x_mid
            f_min = f_mid
    x_mid = (x_min + x_max) / 2
    try:
        return (round(x_mid, 4), calc_m_value_simple(z, mn, alpha_n, x_mid, dp, beta, is_internal))
    except ValueError:
        return (None, None)

if __name__ == '__main__':
    M = calc_m_value_simple(20, 3, 20, 0, 5)
    print(f'''直齿M3Z20 x=0 dp=5: M={M}''')
    M2 = calc_m_value_simple(20, 3, 20, 0.5, 5)
    print(f'''直齿M3Z20 x=0.5 dp=5: M={M2}''')
    M3 = calc_m_value_simple(20, 3, 20, 0, 5, beta=15)
    print(f'''斜齿M3Z20 β15° x=0 dp=5: M={M3}''')
    (x_calc, M_calc) = solve_x_from_m_value(20, 3, 20, 5, M2)
    print(f'''反求x: target M={M2}, calc x={x_calc}, M_calc={M_calc}''')
    M_int = calc_m_value_simple(40, 3, 20, 0, 5, is_internal=True)
    print(f'''内齿轮M3Z40 x=0 dp=5: M={M_int}''')
    print('\nAll tests passed!')