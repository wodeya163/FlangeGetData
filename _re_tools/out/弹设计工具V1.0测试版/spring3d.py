# Reconstructed from bytecode by split_decompile.py
# spring3d.pyc

'''SpringTool 三维模型导出模块（V1：压缩弹簧）。

几何：圆截面钢丝沿变节距螺旋线扫掠成管状实体（刻面逼近）；
端圈按并紧处理（死圈节距 = 线径 d，两端各 1 死圈，与计算模块 n1=n+2 一致）。

导出格式：
- 二进制 STL（.stl）：全 CAD 通用，体积小
- AP214 STEP（.stp/.step）：**光滑 B 样条曲面实体**（见 spring_nurbs_step）
  —— 管身是真曲面，一根弹簧 3~5 张面；光滑链路失败时退回刻面多面体
  （每三角形一个 ADVANCED_FACE，共享边拓扑，CLOSED_SHELL + MANIFOLD_SOLID_BREP）

诚实声明：光滑版是 B 样条**逼近**（螺旋线是超越曲线，无法用多项式精确表示），
实测到解析螺旋管面的最大偏差在**线径的 0.5% 以内**（详见 _nurbs_proto.py 的 P4）。
STL 只有刻面一种写法，圆截面按 16 边形、螺旋线每圈 48 段逼近。
'''
import math
import os
import struct
from datetime import datetime
SEG_WIRE = 16
PTS_PER_TURN = 48

def _pitch_and_bounds(d, H0, n, nt):
    '''返回 (p, nd)。p=有效圈节距，nd=每端死圈数（可非整数）。
    端圈并紧：死圈节距 = d；总升高 = d*死圈总数 + p*n = H0 - d。'''
    if nt < n:
        raise ValueError(f'''总圈数 {nt} 小于有效圈数 {n}，无法生成三维模型''')
    p = (H0 - d - d * (nt - n)) / n
    if p < d:
        raise ValueError(f'''自由高度 H0={H0:.2f} 下有效圈节距 p={p:.2f} 小于线径 d={d}（低于压并高度），无法生成三维模型''')
    return (p, (nt - n) / 2)
def _centerline_z(theta, d, H0, n, nt, p, nd):
    '''钢丝中心线 z 坐标（分段线性节距）。theta 单位弧度。'''
    per = 2 * math.pi
    t_dead = per * nd
    t_act = per * n
    if theta <= t_dead:
        return d / 2 + d * theta / per
    if None <= t_dead + t_act:
        return d / 2 + d * nd + p * (theta - t_dead) / per
    return None / 2 + d * nd + p * n + d * (theta - t_dead - t_act) / per
def _centerline_dz(theta, d, n, nt, p, nd):
    '''dz/dtheta（分段常数），用于切向量。'''
    per = 2 * math.pi
    t_dead = per * nd
    t_act = per * n
    if theta <= t_dead or theta > t_dead + t_act:
        return d / per
    return None / per
def build_compression_mesh(d, D, n, H0, nt, seg, ppt):
    '''生成压缩弹簧刻面网格。

    参数：d 线径 / D 中径 / n 有效圈数 / H0 自由高度 / nt 总圈数(默认 n+2)
    返回：(verts, faces)；verts 为 [(x,y,z)]（mm），faces 为 [(a,b,c)] 顶点索引，
    三角形按外法线逆时针定向（已做体积符号自检）。'''
    if not nt is not None:
        nt = n + 2
    if d <= 0 and D <= 0 and n <= 0 or H0 <= 0:
        raise ValueError('d/D/n/H0 必须为正数')
    (p, nd) = _pitch_and_bounds(d, H0, n, nt)
    R = D / 2
    r = d / 2
    per = 2 * math.pi
    n_ring = max(int(round(ppt * nt)), 8)
    verts = []
    ring_start = []
    for i in range(n_ring + 1):
        theta = per * nt * i / n_ring
        cy = R * math.sin(theta)
        cx = R * math.cos(theta)
        cz = _centerline_z(theta, d, H0, n, nt, p, nd)
        dz = _centerline_dz(theta, d, n, nt, p, nd)
        tz = dz
        ty = R * math.cos(theta)
        tx = -R * math.sin(theta)
        tn = math.sqrt(tx * tx + ty * ty + tz * tz)
        tz = tz / tn
        ty = ty / tn
        tx = tx / tn
        uy = -math.sin(theta)
        ux = -math.cos(theta)
        dot = ux * tx + uy * ty
        ez = -dot * tz
        ey = uy - dot * ty
        ex = ux - dot * tx
        en = math.sqrt(ex * ex + ey * ey + ez * ez)
        ez = ez / en
        ey = ey / en
        ex = ex / en
        bx = ty * ez - tz * ey
        by = tz * ex - tx * ez
        bz = tx * ey - ty * ex
        ring_start.append(len(verts))
        for j in range(seg):
            phi = 2 * math.pi * j / seg
            s = math.sin(phi) * r
            c = math.cos(phi) * r
            verts.append((cx + c * ex + s * bx, cy + c * ey + s * by, cz + c * ez + s * bz))
            faces = []
            for i in range(n_ring):
                a0 = ring_start[i]
                b0 = ring_start[i + 1]
                for j in range(seg):
                    j2 = (j + 1) % seg
                    v01 = a0 + j2
                    v00 = a0 + j
                    v11 = b0 + j2
                    v10 = b0 + j
                    faces.append((v00, v10, v11))
                    faces.append((v00, v11, v01))
                    for ring, is_top in ((0, False), (n_ring, True)):
                        theta = per * nt if is_top else 0
                        cz = _centerline_z(theta, d, H0, n, nt, p, nd)
                        c_idx = len(verts)
                        verts.append((R * math.cos(theta), R * math.sin(theta), cz))
                        base = ring_start[ring]
                        for j in range(seg):
                            j2 = (j + 1) % seg
                            if is_top:
                                faces.append((c_idx, base + j2, base + j))
                                continue
                            faces.append((c_idx, base + j, base + j2))
                            if _signed_volume(verts, faces) < 0:
                                faces = faces()
    return (verts, faces)
def _signed_volume(verts, faces):
    '''散度定理有向体积（mm³）。'''
    v6 = 0
    for a, b, c in faces:
        (ax, ay, az) = 
        (bx, by, bz) = verts[a], verts[b], verts[c]
        (cx, cy, cz) = None
        v6 += ax * (by * cz - bz * cy) + ay * (bz * cx - bx * cz) + az * (bx * cy - by * cx)
        return v6 / 6
def mesh_stats(verts, faces):
    '''网格体检：流形性、体积、包围盒。manifold=每条无向边恰被 2 个三角形共享。'''
    edge_count = { }
    for a, b, c in faces:
        for u, v in ((a, b), (b, c), (c, a)):
            k = (u, v) if u < v else (v, u)
            edge_count[k] = edge_count.get(k, 0) + 1
            bad = edge_count.items()()
            xs = verts()
            ys = verts()
            zs = verts()
            return {
                'manifold': not bad,
                'bad_edges': len(bad),
                'vertices': len(verts),
                'faces': len(faces),
                'volume': _signed_volume(verts, faces),
                'bbox': (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)) }
def write_stl(path, verts, faces, header):
    h = header[:80].ljust(80, b'\x00')
    tris = bytearray()
    for a, b, c in faces:
        (ax, ay, az) = 
        (bx, by, bz) = verts[a], verts[b], verts[c]
        (cx, cy, cz) = None
        uz = bz - az
        uy = by - ay
        ux = bx - ax
        vz = cz - az
        vy = cy - ay
        vx = cx - ax
        nz = ux * vy - uy * vx
        ny = uz * vx - ux * vz
        nx = uy * vz - uz * vy
        if not math.sqrt(nx * nx + ny * ny + nz * nz):
            nl = 1
            tris += struct.pack('<3f', nx / nl, ny / nl, nz / nl)
            tris += struct.pack('<3f', ax, ay, az)
            tris += struct.pack('<3f', bx, by, bz)
            tris += struct.pack('<3f', cx, cy, cz)
            tris += struct.pack('<H', 0)
            continue
            f = open(path, 'wb')
            f.write(h)
            f.write(struct.pack('<I', len(faces)))
            f.write(tris)
            None(None, None)
            return None
        with None:
            if not math.sqrt(nx * nx + ny * ny + nz * nz):
                pass
def _fmt(x):
    '''STEP 实数：固定 6 位小数，消除 -0.000000。'''
    if abs(x) < 5e-07:
        x = 0
    return f'''{x:.6f}'''
class _StepBuilder:
    '''STEP 实体累加器：add(TYPE, params) 返回 id，最终写 DATA 段。'''

    def __init__(self):
        self.lines = []
        self.n = 0
    def add(self, etype, params):
        self.lines.append(f'''#{self.n}={etype}({params});''')
        return self.n
    def add_multi(self, text_lines):
        """跨行实体（如巨型 CLOSED_SHELL）。text_lines 每行自带换行。
            注意：必须显式补上实体终止符 ';' —— 曾漏掉导致文件非法。"""
        self.lines.append(f'''#{self.n}=''' + ''.join(text_lines) + ';')
        return self.n
def _ascii_safe(s):
    """把字符串限制为可打印 ASCII（STEP 头段用）。

    起因：中文文件名写入 FILE_NAME 时，文件里出现非 ASCII 字节，UG/NX 等严格
    解析器会读不进去。这里把非 ASCII 字符替换成 '_'，保证整份 STEP 是纯 ASCII。
    """
    return (lambda .0: for ch in .0:
if  <= 32, ord(ch) or 32, ord(ch) < 127:
pass'_'chcontinue)(s())
def write_step(path, verts, faces, name, simple_units):
    '''AP214 刻面 STEP：共享边拓扑的闭合流形实体。

    simple_units=False（默认，交付用）：单位/上下文用复合实体实例
    （LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(...)，主流 CAD 标准写法）。
    simple_units=True：退化为简单实体实例，仅供语法解析器（steputils 不支持复合
    实体，已用最小样本证实）做全量解析校验，不用于交付。
    '''
    name = _ascii_safe(name)
    b = _StepBuilder()
    vpt = verts()
    vvx = range(len(verts))()
    edges = { }
    ekeys = []
    for a, bb, c in faces:
        for u, v in ((a, bb), (bb, c), (c, a)):
            k = (u, v) if u < v else (v, u)
            if k not in edges:
                edges[k] = None
                ekeys.append(k)
            for u, v in ekeys:
                (ax, ay, az) = 
                (bx, by, bz) = verts[u], verts[v]
                dz = bz - az
                dy = by - ay
                dx = bx - ax
                ln = math.sqrt(dx * dx + dy * dy + dz * dz)
                dz = dz / ln
                dy = dy / ln
                dx = dx / ln
                d_dir = b.add('DIRECTION', f'''\'\',({_fmt(dx)},{_fmt(dy)},{_fmt(dz)})''')
                d_vec = b.add('VECTOR', f'''\'\',#{d_dir},{_fmt(ln)}''')
                d_line = b.add('LINE', f'''\'\',#{vpt[u]},#{d_vec}''')
                edges[(u, v)] = b.add('EDGE_CURVE', f'''\'\',#{vvx[u]},#{vvx[v]},#{d_line},.T.''')
                face_ids = []
                for a, bb, c in faces:
                    (ax, ay, az) = 
                    (bx, by, bz) = verts[a], verts[bb], verts[c]

                    def (cx, cy, cz)(.0 = None):
                        '''VERTEX_POINT'''
                        return [ b.add('VERTEX_POINT', f'''\'\',#{vpt[i]}''') for i in .0 ]

                    uz = bz - az
                    uy = by - ay
                    ux = bx - ax
                    vz = cz - az
                    vy = cy - ay
                    vx = cx - ax
                    nz = ux * vy - uy * vx
                    ny = uz * vx - ux * vz
                    nx = uy * vz - uz * vy
                    nl = math.sqrt(nx * nx + ny * ny + nz * nz)
                    if nl < 1e-12:
                        raise ValueError('退化三角形（零面积），无法生成 STEP')
                    nz = nz / nl
                    ny = ny / nl
                    nx = nx / nl
                    oz = (az + bz + cz) / 3
                    oy = (ay + by + cy) / 3
                    ox = (ax + bx + cx) / 3
                    xl = math.sqrt(ux * ux + uy * uy + uz * uz)
                    xz = uz / xl
                    xy = uy / xl
                    xx = ux / xl
                    d_z = b.add('DIRECTION', f'''\'\',({_fmt(nx)},{_fmt(ny)},{_fmt(nz)})''')
                    d_x = b.add('DIRECTION', f'''\'\',({_fmt(xx)},{_fmt(xy)},{_fmt(xz)})''')
                    d_o = b.add('CARTESIAN_POINT', f'''\'\',({_fmt(ox)},{_fmt(oy)},{_fmt(oz)})''')
                    pl = b.add('AXIS2_PLACEMENT_3D', f'''\'\',#{d_o},#{d_z},#{d_x}''')
                    plane = b.add('PLANE', f'''\'\',#{pl}''')
                    oes = []
                    for u, v in ((a, bb), (bb, c), (c, a)):
                        forward = u < v
                        k = (u, v) if forward else (v, u)
                        oes.append(b.add('ORIENTED_EDGE', f'''\'\',*,*,#{edges[k]},{'.T.' if forward else '.F.'}'''))
                        loop = 'EDGE_LOOP'("'',(", f'''{','.join}{(lambda .0: for o in .0:
f'''#{o}'''None)(oes())})''')
                        bound = b.add('FACE_OUTER_BOUND', f'''\'\',#{loop},.T.''')
                        face_ids.append(b.add('ADVANCED_FACE', f'''\'\',(#{bound}),#{plane},.T.'''))
                        app_ctx = b.add('APPLICATION_CONTEXT', "'core data for automotive mechanical design processes'")
                        b.add('APPLICATION_PROTOCOL_DEFINITION', f'''\'international standard\',\'automotive_design\',2000,#{app_ctx}''')
                        pd_ctx = b.add('PRODUCT_DEFINITION_CONTEXT', f'''\'part definition\',#{app_ctx},\'design\'''')
                        prod_ctx = b.add('PRODUCT_CONTEXT', f'''\'\',#{app_ctx},\'mechanical\'''')
                        prod = b.add('PRODUCT', f'''\'{name}\',\'{name}\',\'\',({{}})''')
                        b.lines[prod - 1] = f'''#{prod}=PRODUCT(\'{name}\',\'{name}\',\'\',(#{prod_ctx}));'''
                        pdf = b.add('PRODUCT_DEFINITION_FORMATION', f'''\'\',\'\',#{prod}''')
                        pdef = b.add('PRODUCT_DEFINITION', f'''\'design\',\'\',#{pdf},#{pd_ctx}''')
                        pds = b.add('PRODUCT_DEFINITION_SHAPE', f'''\'\',\'\',#{pdef}''')

                        def complex_add(parts):
                            '''写复合实体，用「内部映射」：外层括号 + 每个分支独占一行。

                                起因：之前用一行拼接的外部映射（LENGTH_UNIT()NAMED_UNIT(*)SI_UNIT(...)），
                                UG/NX 读盘日志直接报 "Expecting \';\', found NAMED_UNIT instead"，
                                单位/上下文整段读不进去。NX 自己导出的参考文件也是括号包裹的内部映射。
                                '''
                            '#%d=(\n' % b.n(''.join + (lambda .0: for p in .0:
                        p + '\n'None)(parts()) + ');')
                            return b.n
                        if simple_units:
                            lu = b.add('SI_UNIT', '.MILLI.,.METRE.')
                            pau = b.add('PLANE_ANGLE_UNIT', '')
                            sau = b.add('SOLID_ANGLE_UNIT', '')
                            grc = b.add('GEOMETRIC_REPRESENTATION_CONTEXT', '3')
                        else:
                            lu = complex_add([
                                'LENGTH_UNIT()',
                                'NAMED_UNIT(*)',
                                'SI_UNIT(.MILLI.,.METRE.)'])
                            pau = complex_add([
                                'NAMED_UNIT(*)',
                                'PLANE_ANGLE_UNIT()',
                                'SI_UNIT($,.RADIAN.)'])
                            sau = complex_add([
                                'NAMED_UNIT(*)',
                                'SI_UNIT($,.STERADIAN.)',
                                'SOLID_ANGLE_UNIT()'])
                            unc = b.add('UNCERTAINTY_MEASURE_WITH_UNIT', f'''LENGTH_MEASURE(1.E-07),#{lu},\'distance_accuracy_value\',\'confusion accuracy\'''')
                            grc = complex_add([
                                'GEOMETRIC_REPRESENTATION_CONTEXT(3)',
                                'GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#%d))' % unc,
                                'GLOBAL_UNIT_ASSIGNED_CONTEXT((#%d,#%d,#%d))' % (lu, pau, sau),
                                "REPRESENTATION_CONTEXT('Context #1','3D Context')"])
    refs_text = (lambda .0: for i in .0:
f'''#{i}'''None)(face_ids())
    chunks = []
    pos = 0
    total = len(refs_text)
    if pos < total:
        end = min(pos + 200, total)
        if end < total:
            if end > pos and refs_text[end] != ',':
                end -= 1
                if end > pos:
                    if not refs_text[end] != ',':
                        end += 1
                        pos = end
                        if (pos < total or chunks) and chunks[-1].endswith(','):
                            raise ValueError('面引用列表出现尾逗号（Part 21 不允许）')
                        shell = [
                            f'''CLOSED_SHELL(\'{name}\',(\n''']((lambda .0: [ c + '\n' for c in .0 ]) + chunks() + [
                            '))'])
                        solid = b.add('MANIFOLD_SOLID_BREP', f'''\'{name}\',#{shell}''')
                        absr = b.add('ADVANCED_BREP_SHAPE_REPRESENTATION', f'''\'\',(#{solid}),#{grc}''')
                        b.add('SHAPE_DEFINITION_REPRESENTATION', f'''#{pds},#{absr}''')
                        f = open(path, 'w', encoding = 'utf-8', newline = '\n')
                        f.write('ISO-10303-21;\n')
                        f.write('HEADER;\n')
                        f.write("FILE_DESCRIPTION(('SpringTool faceted compression spring'),'2;1');\n")
                        ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                        fname = _ascii_safe(os.path.basename(path))
                        f.write(f'''FILE_NAME(\'{fname}\',\'{ts}\',(\'\'),(\'\'),\'SpringTool\',\'SpringTool\',\'\');\n''')
                        f.write("FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));\n")
                        f.write('ENDSEC;\n')
                        f.write('DATA;\n')
                        for ln in b.lines:
                            f.write(ln + '\n')
                            f.write('ENDSEC;\nEND-ISO-10303-21;\n')
                            b.add_multi(None, None)
                            return None
                            with None:
                                if not pos < total:
                                    pass
    refs_text[end] != ','
    ','.join
def export(path, d, D, n, H0, nt, seg, ppt, simple_units, smooth):
    '''按扩展名导出。返回统计 dict（含 mode：smooth / faceted）。

    .stp/.step 默认走**光滑 B 样条曲面**（spring_nurbs_step）：一根弹簧 3~5 张面
    且是曲面实体，导入 UG 后不是三角面片。若光滑链路抛异常，退回刻面版，并把
    原因写进返回值的 "fallback" —— 不静默降级，界面会把原因告诉用户。
    .stl 只有刻面一种写法（STL 格式本身没有曲面），不受 smooth 影响。
    '''
    ext = os.path.splitext(path)[1].lower()
    if ext == '.stl':
        (verts, faces) = build_compression_mesh(d, D, n, H0, nt = nt, seg = seg, ppt = ppt)
        write_stl(path, verts, faces)
        stats = mesh_stats(verts, faces)
        stats['file_size'] = os.path.getsize(path)
        stats['mode'] = 'faceted'
        return stats
    if None not in ('.stp', '.step'):
        raise ValueError(f'''不支持的扩展名 {ext}（支持 .stl / .stp / .step）''')
    if smooth:

        try:
            import spring_nurbs_step as SNS
            st = SNS.export_smooth(path, d, D, n, H0, nt = nt, simple_units = simple_units)
            st['mode'] = 'smooth'
            return st
        except Exception:
            e = None
            fallback = f'''{type(e).__name__!s}: {e!s}'''
            e = None
            del e
        except:
            e = None
            del e

        (verts, faces) = build_compression_mesh(d, D, n, H0, nt = nt, seg = seg, ppt = ppt)
        write_step(path, verts, faces, simple_units = simple_units)
        stats = mesh_stats(verts, faces)
        stats['file_size'] = os.path.getsize(path)
        stats['mode'] = 'faceted'
        stats['fallback'] = fallback
        return stats
    (verts, faces) = None(d, D, n, H0, nt = nt, seg = seg, ppt = ppt)
    write_step(path, verts, faces, simple_units = simple_units)
    stats = mesh_stats(verts, faces)
    stats['file_size'] = os.path.getsize(path)
    stats['mode'] = 'faceted'
    return stats

