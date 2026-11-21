# Reconstructed from bytecode by split_decompile.py
# spring_nurbs.pyc

'''螺旋管的 B 样条曲面表达（用于输出光滑 STEP，替代刻面多面体）。

为什么要有这个模块
------------------
刻面写法（spring3d 原方案）把钢丝圆截面离散成 16 边形、螺旋每圈 48 段，
每个四边形再拆 2 个三角形，一根弹簧出 15392 个**平面三角面**。导入 UG 后是
多面体：看着是三角面片，倒角/抽壳这类操作也做不了。

本模块把螺旋管表达成**一整张双三次 B 样条曲面**：

1. 在 (t, φ) 参数网格上采样螺旋管表面点；
2. u 向（沿螺旋）做 clamp 三次插值；
3. v 向（绕截面一周）做**闭环**三次插值 —— 用周期条件（首尾重合 + C1 + C2）
   解出控制点，得到的样条首尾控制点重合、接缝处天然 C2，不留折痕；
4. 拓扑按圆柱体的标准写法：管身 1 个面（用一条接缝边在边环里出现两次，
   把两个端面环连成一个环），两端各 1 个平面封盖。

结果：**3 个面**（刻面版 15392 个），且面是真曲面，导入 UG 后是光滑实体。

关于接缝的做法（踩过的坑）
--------------------------
最初的写法是「周向也用 clamp 样条、采样点首尾各留一个重合点」，结果接缝处
首尾切向对不上，实测折角 11.58°，导入后能看到一条棱。改成周期条件求解后，
闭合与 C2 都是构造性保证的，不再依赖参数化碰巧对称。
'''
import math
import spring3d
DEG = 3
KNOT_SPEC = 'UNSPECIFIED'

def _basis(i, p, u, U):
    '''Cox-de Boor 递推求 N_{i,p}(u)。'''
    if p == 0:
        if  <= U[i], u or U[i], u < U[i + 1]:
            pass

    else:
        return 1
    if None(u - U[-1]) < 1e-15 and abs(U[i + 1] - U[-1]) < 1e-15:
        return 1
    return None
    U[i + p] - U[i] = 0
    if d1 > 1e-15:
        a = ((u - U[i]) / d1) * _basis(i, p - 1, u, U)
    b = 0
    d2 = U[i + p + 1] - U[i + 1]
    if d2 > 1e-15:
        b = ((U[i + p + 1] - u) / d2) * _basis(i + 1, p - 1, u, U)
    return a + b
def _find_span(u, p, U):
    pass


def _basis_funs(span, u, p, U):
    '''NURBS Book A2.2：返回非零基函数 N[0..p]。'''
    N = [
        0] * (p + 1)
    left = [
        0] * (p + 1)
    right = [
        0] * (p + 1)
    N[0] = 1
    for j in range(1, p + 1):
        left[j] = u - U[span + 1 - j]
        right[j] = U[span + j] - u
        saved = 0
        for r in range(j):
            temp = N[r] / (right[r + 1] + left[j - r])
            N[r] = saved + right[r + 1] * temp
            saved = left[j - r] * temp
            N[j] = saved
            return N
def _solve(A, b):
    '''带部分选主元的高斯消元（规模小，稳健优先）。'''
    n = len(b)
    for k in range(n):
        pr = k
        piv = abs(A[k][k])
        for r in range(k + 1, n):
            if abs(A[r][k]) > piv:
                pr = r
                piv = abs(A[r][k])
            if piv < 1e-14:
                raise ValueError('插值矩阵奇异（采样点过近？）')
            if pr != k:
                A[k], A[pr] = A[pr], A[k]
                b[k], b[pr] = b[pr], b[k]
        for r in range(k + 1, n):
            f = A[r][k] / A[k][k]
            if f == 0:
                continue
            for c in range(k, n):
                [
                    0] * n = None
                for k in range(n - 1, -1, -1):
                    v = b[k]
                    for c in range(k + 1, n):
                        v -= A[k][c] * x[c]
                        x[k] = v / A[k][k]
                        return x
def _band_build(s, p, U):
    '''组装带状配置矩阵：Ab[k][j] = N_{k-p+j,p}(s_k)，j = 0..2p。

    每行只有 p+1 个非零基函数（N_{span-p..span}），所以确实落在带宽 p 内。
    用 A2.2 一次算出整行，比逐个调 Cox-de Boor 递推快一个量级。
    '''
    n = len(s) - 1
    W = 2 * p + 1
    Ab = range(n + 1)()
    for k in range(n + 1):
        sp = _find_span(s[k], p, U)
        N = _basis_funs(sp, s[k], p, U)
        row = Ab[k]
        for a in range(p + 1):
            j = ((sp - p) + a - k) + p
            if  <= 0, j or 0, j < W:
                pass
            else:
                (lambda .0 = None: [ [
0] * W for _ in .0 ])
            return Ab
def _band_factor(Ab, p):
    '''带状 LU 分解（原地），不选主元。

    为什么敢不选主元：B 样条配置矩阵在满足 Schoenberg-Whitney 条件时是**全正
    矩阵**，不选主元的高斯消元数值稳定。而选主元会把带状结构撑破，退化成 O(n³)
    稠密求解 —— 段数上到 300+ 时稠密解法根本跑不完。
    '''
    n = len(Ab)
    for k in range(n):
        piv = Ab[k][p]
        if abs(piv) < 1e-14:
            raise ValueError('带状主元过小（%g）：节点与插值参数分布不匹配' % piv)
        for r in range(k + 1, min(n, k + p + 1)):
            jk = p - r - k
            f = Ab[r][jk] / piv
            if f == 0:
                continue
            Ab[r][jk] = f
            for c in range(k + 1, min(n, r + p + 1)):
                jc = (c - k) + p
                if jc < 2 * p + 1:
                    jr = (c - r) + p
                    if  <= 0, jr or 0, jr < 2 * p + 1:
                        pass

                return Ab
def _band_solve(Ab, rhs, p):
    '''用 _band_factor 分解好的带矩阵回代。rhs 会被就地修改，传副本进来。'''
    n = len(Ab)
    b = list(rhs)
    for k in range(n):
        for r in range(k + 1, min(n, k + p + 1)):
            [
                0] * n = None
            for k in range(n - 1, -1, -1):
                v = b[k]
                for c in range(k + 1, min(n, k + p + 1)):
                    v -= Ab[k][(c - k) + p] * x[c]
                    x[k] = v / Ab[k][p]
                    return x
def _knots_avg(s, p):
    '''A9.3 平均法节点向量（两端 clamp）。s 为参数，长度 n+1。

    注意：平均法会让**首尾两个节点区间是内部区间的两倍宽**（第一个内节点取
    (s1+s2+s3)/3，重心落在 s2，离 s0 有 2h）。首末区间的插值误差按 h⁴ 走，
    宽度翻倍就是 16 倍 —— 实测精度最差处总在段的两端，根子在这里。
    '''
    n = len(s) - 1
    if n < p:
        raise ValueError('数据点太少，无法构造 %d 次样条' % p)
    U = [
        0] * (p + 1)
    for None in range(1, (n - p) + 1):
        k = None
        U += [
            1] * (p + 1)
        return U
def _knots_uniform_span(s, p):
    '''等宽节点向量：把 [s0, sn] 均分成 (n-p+1) 段，两段不再翻倍。

    代价：不随 s 的分布自适应。**只有 s 本身也是均匀的时候才安全** —— 参数
    s 若按弦长取（非均匀），等宽节点可能破坏 Schoenberg-Whitney 条件，矩阵
    虽然不奇异，解却会局部炸开（实测 0.28mm 级）。所以本函数必须配均匀参数用。
    '''
    n = len(s) - 1
    if n < p:
        raise ValueError('数据点太少，无法构造 %d 次样条' % p)
    m = (n - p) + 1
    U = [
        0] * (p + 1)
    for k in range(1, (n - p) + 1):
        U.append(float(k) / m)
        U += [
            1] * (p + 1)
        return U
_KNOTS = {
    'avg': _knots_avg,
    'uniform_span': _knots_uniform_span }

def _interp_factor(s, p, knots):
    '''按给定参数 s 造节点向量并做带状 LU 分解，返回 (Ab, U)。

    u 向每一列 φ 用的是**同一套 s 和 U**，配置矩阵也就同一份；这里只分解一次，
    后面 3×Nv 个右端项都靠回代解决，省掉 Nv 次重复分解。
    '''
    U = _KNOTS[knots](s, p)
    Ab = _band_build(s, p, U)
    _band_factor(Ab, p)
    return (Ab, U)
def _interp_curve(Q, s, p, knots):
    '''开曲线插值：给定数据点 Q 与参数 s，返回 (clamp 控制点, 节点向量)。'''
    n = len(Q) - 1
    dim = len(Q[0])
    (Ab, U) = _interp_factor(s, p, knots)
    P = range(n + 1)()
    for sol in range(dim):
        dd = None

        def <listcomp>(.0 = None):
            return [ Q[k][dd] for k in .0 ]

        for i in range(n + 1):
            P[i][dd] = sol[i]
            return (P, U)
def _closed_interp_curve(Q, p):
    '''闭环曲线插值：N 个循环数据点，均匀节点，返回 (控制点, 节点向量)。

    输出的样条**两端 clamp**（标准写法，CAD 读盘不会误解），但接缝处满足：
      位置重合  D[n]   = D[0]
      一阶连续  D[n-1] = 2*D[0] - D[1]
      二阶连续  D[n-2] = 6*D[0] - 6*D[1] + D[2]
    这三条是周期条件，代入后自由未知量只剩 D[0..N-1]，与 N 个插值条件正好配平。

    控制点数 = N + p（p=3 时 N+3），节点向量 = 0×4, 1/N..(N-1)/N, 1×4。
    '''
    N = len(Q)
    if N < p + 1:
        raise ValueError('闭环插值至少需要 %d 个点' % (p + 1))
    h = 1 / N
    U = (lambda .0 = None: [ k * h for k in .0 ]) + range(1, N)() + [
        1] * (p + 1)
    n = N + p - 1
    dim = len(Q[0])
    dep = {
        n - 2: [
            (0, 6),
            (1, -6),
            (2, 1)],
        n - 1: [
            (0, 2),
            (1, -1)],
        n: [
            (0, 1)] }
    nfree = N
    A = range(N)()
    for j in range(N):
        u = j * h
        row = A[j]
        for i in range(nfree):
            row[i] = _basis(i, p, u, U)
            for bf in dep.items():
                (i, terms) = None
                if bf == 0:
                    continue
                for k, c in terms:

                    def [
                        None] * (n + 1)(.0 = None):
                        return [ [
                            0] * nfree for _ in .0 ]

                    for rhs in range(dim):
                        dd = None
                        sol = (lambda .0: [ r[:] for r in .0 ])(A(), rhs)
                        for i in range(nfree):
                            if not D[i] is not None:
                                D[i] = [
                                    0] * dim
                            D[i][dd] = sol[i]
                            for None in dep.items():
                                (i, terms) = None
                                D[i] = range(dim)()
                                return (D, U)
def eval_point(P, U, V, u, v, p, q):
    '''求曲面点 S(u, v)。P[i][j]，i 沿 u，j 沿 v。'''
    iu = _find_span(u, p, U)
    iv = _find_span(v, q, V)
    Nu = _basis_funs(iu, u, p, U)
    Nv = _basis_funs(iv, v, q, V)
    out = [
        0,
        0,
        0]
    for a in range(p + 1):
        wa = Nu[a]
        if wa == 0:
            continue
        row = P[(iu - p) + a]
        for bb in range(q + 1):
            w = wa * Nv[bb]
            if w == 0:
                continue
            pt = row[(iv - q) + bb]
            return tuple(out)
def eval_uv(P, U, V, u, v, h, p, q):
    '''返回 (点, ∂u, ∂v)。偏导用中心差分（坐标量级几十 mm，精度足够定向判定）。'''
    pu = range(3)()
    pv = range(3)()
    return (eval_point(P, U, V, u, v, p, q), tuple(pu), tuple(pv))
def _frame(t, d, D, n, H0, nt, p, nd):
    '''返回 (中心点 C, e1, e2, 切向 T)。与 spring3d 的网格标架同一套 e1。

    e2 取 e1 × T（不是 T × e1）：这样 ∂u×∂v 恰好指向管外，STEP 里
    ADVANCED_FACE 的 same_sense 可以直接写 .T.，不用再翻一次。
    '''
    R = D / 2
    cy = R * math.sin(t)
    cx = R * math.cos(t)
    cz = spring3d._centerline_z(t, d, H0, n, nt, p, nd)
    dz = spring3d._centerline_dz(t, d, n, nt, p, nd)
    tz = dz
    ty = R * math.cos(t)
    tx = -R * math.sin(t)
    tl = math.sqrt(tx * tx + ty * ty + tz * tz)
    tz = tz / tl
    ty = ty / tl
    tx = tx / tl
    uy = -math.sin(t)
    ux = -math.cos(t)
    dot = ux * tx + uy * ty
    ez = -dot * tz
    ey = uy - dot * ty
    ex = ux - dot * tx
    el = math.sqrt(ex * ex + ey * ey + ez * ez)
    ez = ez / el
    ey = ey / el
    ex = ex / el
    bx = ey * tz - ez * ty
    by = ez * tx - ex * tz
    bz = ex * ty - ey * tx
    return ((cx, cy, cz), (ex, ey, ez), (bx, by, bz), (tx, ty, tz))
def _surf_point(t, phi, d, D, n, H0, nt, p, nd):
    '''解析螺旋管表面点：C(t) + r(cos φ·e1 + sin φ·e2)。'''
    (C, e1, e2, _T) = _frame(t, d, D, n, H0, nt, p, nd)
    r = d / 2
    return (C[0] + r * (math.cos(phi) * e1[0] + math.sin(phi) * e2[0]), C[1] + r * (math.cos(phi) * e1[1] + math.sin(phi) * e2[1]), C[2] + r * (math.cos(phi) * e1[2] + math.sin(phi) * e2[2]))
def _u_params(Q, Nv, mode):
    '''u 向参数：对每个 j 做弦长参数化后取平均（A9.4）。

    螺旋管表面在 (t,φ) 上的真实速度随 φ 变化（迎风侧快、背风侧慢），若直接按 t
    等分取参数，插值曲线会在段间多出一项二阶误差。弦长参数化可恢复四次收敛。

    mode="uniform" 时直接按 t 等分取参数。为什么它其实很接近弦长：螺旋中心线
    |C\'(t)| = sqrt(R² + c²) 是常数，沿 t 等分就是沿中心线弧长等分；表面点比中心线
    多出的那点速度差是 O(r/R) 量级。实测两种参数化的精度差在 1e-3 mm 以下，但
    **均匀参数能配等宽节点**（等宽节点不自适应，非均匀参数会破坏 Schoenberg-
    Whitney 条件），换来的是首末不再翻倍的节点区间 —— 这笔账划算。
    '''
    nu = len(Q) - 1
    if mode == 'uniform':
        return range(nu + 1)()
    su = [
        None] * (nu + 1)
    for j in range(Nv):
        acc = [
            0]
        for i in range(1, nu + 1):
            bpt = Q[i][j]
            a = Q[i - 1][j]
            acc.append(acc[-1] + math.dist(a, bpt))
            if not acc[-1]:
                tot = 1
                for i in range(nu + 1):
                    return su()
def _piece(ts, d, D, n, H0, nt, p, nd, Nv, knots, umode):
    '''在 t 序列 ts 上造一段管身曲面。

    u 向（沿螺旋）配置矩阵对所有 φ 列是同一份，这里分解一次后逐列回代；
    v 向（绕截面一周）是闭环插值，规模只有 Nv（≤32），稠密求解足够。
    '''
    Q = ts()
    su = _u_params(Q, Nv, umode)
    (Ab, U) = _interp_factor(su, DEG, knots)
    R = range(len(ts))()
    for None in range(Nv):
        j = None
        for sol in range(3):
            dd = None

            def <listcomp>(.0 = None):
                return [ Q[i][j][dd] for i in .0 ]

            for i in range(len(ts)):
                R[i][j][dd] = sol[i]
                P = [
                    None] * len(ts)
                V = None
                for i in range(len(ts)):
                    (P[i], V) = _closed_interp_curve(R[i], DEG)
                    nu = len(ts) - 1
                    nv = Nv + DEG - 1
                    return {
                        'P': None,
                        'U': None,
                        'V': None,
                        'nu': None,
                        'nv': None,
                        'ts': None,
                        'su': (lambda .0 = None: [ P[i][0] for i in .0 ]),
                        'seam': range(nu + 1)(),
                        'ring0': P[0],
                        'ring1': P[nu] }
def auto_seg_per_turn(d, D):
    '''按 D/d 选螺旋方向每圈段数，使逼近误差落在 0.4% 线径以内。

    标度律是量出来的，不是推的：seg=16 时四个算例的「最大偏差 / 中径 R」分别
    6.5e-4、7.4e-4、7.7e-4、7.5e-4 —— 与线径几乎无关，只跟 R 成正比，即
        err(16) ≈ 7.7e-4 · R
    加密时实测收敛介于 h³ 与 h⁴ 之间，这里**按 h³ 保守估计**。
    令 err ≤ 0.004·d（线径的 0.4%，远小于任何线径制造公差）：
        seg ≥ 16 / (10.39·d/D)^(1/3)
    四个算例分别给出 13.7 / 14.7 / 12.5 / 28.7，下限 16、上限 64。
    '''
    if d <= 0 or D <= 0:
        return 16
    x = None * d / D
    if x >= 1:
        return 16
    seg = None / x ** 0.333333
    return int(min(64, max(16, math.ceil(seg - 1e-09))))
def build_tube_surface(d, D, n, H0, nt, seg_per_turn, n_phi, knots, umode):
    '''构造螺旋管的双三次 B 样条曲面（按中心线折点分段）。

    为什么要分段
    ------------
    中心线在「并紧圈 ↔ 有效圈」过渡处切向突变（死圈节距 = d，有效圈节距 = p），
    是个 C0 折角。整根做成一张 C2 曲面时，样条会把折角抹圆 —— 实测 D=120/d=2
    的算例在折点处偏离解析管面 0.40 mm（线径才 2 mm）。按折点切开后，每段内部
    中心线都是光滑螺旋，偏差回到 1e-4 mm 量级。

    seg_per_turn：螺旋方向每圈段数（越大越贴合）
    n_phi       ：截面圆周方向采样点数（闭环插值，段数同此值）

    返回 dict：
      pieces[i]  { P, U, V, nu, nv, seam, ring0, ring1 }，P 为 (nu+1)×(nv+3) 控制点
      rings      共有边界环的控制点，长度 = len(pieces)+1
                 （rings[i] 就是 pieces[i].ring0，也就是 pieces[i-1].ring1 —— 同一份
                  对象，保证相邻段严丝合缝）
      cap0/cap1  封盖 {center, normal}
      faces      面数 = len(pieces) + 2
    '''
    if not nt is not None:
        nt = n + 2
    if not seg_per_turn is not None:
        seg_per_turn = auto_seg_per_turn(d, D)
    if d <= 0 and D <= 0 and n <= 0 or H0 <= 0:
        raise ValueError('d/D/n/H0 必须为正数')
    (p, nd) = spring3d._pitch_and_bounds(d, H0, n, nt)
    t_end = 2 * math.pi * nt
    Nv = max(int(n_phi), 4)
    brk = []
    for [] in (2 * math.pi * nd, 2 * math.pi * (nd + n)):
        tb = None
        if  < 1e-09, tb or 1e-09, tb < t_end - 1e-09:
            pass

        if (lambda .0 = None: for x in .0:
abs(tb - x) > 1e-09None)(brk()):
            brk.append(tb)
        for turns in zip(bounds[:-1], bounds[1:]):
            (ta, tb) = None
            mseg = max(int(round(seg_per_turn * turns)), 3)
            ts = range(mseg + 1)()
            pieces.append(_piece(ts, d, D, n, H0, nt, p, nd, Nv, knots, umode))
            for i in range(1, len(pieces)):
                pieces[i]['ring0'] = pieces[i - 1]['ring1']
                rings = pieces() + [
                    pieces[-1]['ring1']]
                (_C0, _e10, _e20, T0) = _frame(0, d, D, n, H0, nt, p, nd)
                (Cend, _e1e, _e2e, Te) = _frame(t_end, d, D, n, H0, nt, p, nd)
                cap0 = {
                    'center': _C0,
                    'normal': (-T0[0], -T0[1], -T0[2]) }
                cap1 = {
                    'center': Cend,
                    'normal': (Te[0], Te[1], Te[2]) }
                n_ctrl = (lambda .0: for q in .0:
(q['nu'] + 1) * (q['nv'] + 1)None)(pieces())
                return {
                    'pieces': pieces,
                    'rings': rings,
                    'cap0': cap0,
                    'cap1': cap1,
                    'n_ctrl': n_ctrl,
                    'faces': len(pieces) + 2 }

