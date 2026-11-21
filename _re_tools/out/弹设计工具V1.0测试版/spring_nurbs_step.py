# Reconstructed from bytecode by split_decompile.py
# spring_nurbs_step.pyc

'''把 spring_nurbs 的 B 样条曲面写成**光滑** AP214 STEP 实体（不是刻面多面体）。

与刻面版（spring3d.write_step）的区别
------------------------------------
刻面版：每个三角形一个 ADVANCED_FACE + PLANE，一根弹簧上万张平面。
本模块：管身每段一张 B_SPLINE_SURFACE_WITH_KNOTS，两端各一张 PLANE 封盖，
        一根弹簧 **3~5 张面**，且管身是真曲面。

拓扑按「闭合曲面」的标准写法
----------------------------
管身在 v 向（绕截面一周）首尾控制点重合，所以边界是一个环，里面装四条有向边：
    接缝边 .T. → 端环1 .T. → 接缝边 .F. → 端环0 .F.
接缝边在环里出现两次（一正一反），这是 STEP 表达闭合曲面的通行做法，
圆柱面在 NX/SW 导出的文件里也是这么写的。

环的定向由右手定则确定：面法向 = ∂u×∂v（spring_nurbs 已保证指向管外，见 P5），
参数域 [0,1]² 逆时针绕行即为上式的顺序。封盖的两个环在管身环里分别是 .F./.T.，
在封盖环里是 .T./.F.，正好相反 —— 这是流形条件要求的。
'''
import math
import os
from datetime import datetime
import spring3d
import spring_nurbs as SN
_FMT = spring3d._fmt
_ASCII = spring3d._ascii_safe

def _knots_to_step(U):
    '''节点向量 -> (多重度列表, 去重后的节点值列表)。

    两端 clamp 的 4 重节点合并成 multiplicity=4；内部节点均为单重。
    合并后再检查一次格式化后是否仍严格递增 —— 若两个不同节点在 6 位小数下
    打印成同一个值，写出去就是非法节点向量。
    '''
    vals = []
    mult = []
    for u in U:
        if vals and abs(u - vals[-1]) < 1e-12:
            continue
        vals.append(u)
        mult.append(1)

        def vals()(.0):
            return [ _FMT(v) for v in .0 ]

        for a, b in zip(txt[:-1], txt[1:]):
            if a == b:
                raise ValueError(f'''节点向量在 6 位小数下退化：相邻节点 {a!s} == {b!s}''')
            return (mult, vals)
def _pt(b, cache, p):
    '''取（或复用）一个 CARTESIAN_POINT 的 id。'''
    key = (lambda .0: for c in .0:
_FMT(c)None)(p())
    if key not in cache:
        cache[key] = b.add('CARTESIAN_POINT', "'',(%s)" % key)
    return cache[key]
def _bspline_curve(b, cache, ctrl, U, deg):
    '''B 样条曲线实体：控制点 + 节点向量。'''
    ids = ctrl()
    (mult, vals) = _knots_to_step(U)
    return deg(','.join, (lambda .0: for i in .0:
'#%d' % iNone)(ids()) % (','.join, (lambda .0: for m in .0:
str(m)None)(mult()), ','.join, (lambda .0: for v in .0:
_FMT(v)None)(vals())))
def _bspline_surface(b, cache, P, U, V, deg):
    '''B 样条曲面实体：控制点网（外层 u 向，内层 v 向）+ 两条节点向量。

    **属性数是 13 个，不是 14 个** —— 这一条是拿 UG 自己导出的 STEP 当参考
    核对出来的（本机 Desktop\\UG100个经典曲面教程\\8\\55.stp，实体 #730/#977）。

    ISO 10303-42 的 b_spline_surface_with_knots 有两个版本：
      旧版：u_multiplicities, v_multiplicities, u_knots, v_knots, knot_spec（共 5 个）
      新版：u_multiplicities, u_knots, u_knot_spec,
            v_multiplicities, v_knots, v_knot_spec            （共 6 个）
    旧版 5+8=13，新版 6+8=14。NX2007 认**旧版**：写 14 个属性时读盘日志报
    "Expecting 13 attributes, found 29 instead"，并卡在 \'u_knots\' 上
    （u_knots 的位置被 u_knot_spec 顶掉了，后面全部错位）。

    同一份参考文件还确认了控制点网方向：外层列表 = u 向控制点数、内层 = v 向
    （参考里外 45 / 内 4，与其 u 控制点 45、v 控制点 4 对得上）。
    '''
    rows = []
    for i in range(len(P)):
        None(None % (lambda .0 = None: for c in .0:
'#%d' % _pt(b, cache, c)None)(P[i]()))
        (um, uv) = _knots_to_step(U)
        (vm, vv) = _knots_to_step(V)
        return deg(','.join(rows), ','.join % ((lambda .0: for m in .0:
str(m)None)(um()), ','.join, (lambda .0: for m in .0:
str(m)None)(vm()), ','.join, (lambda .0: for v in .0:
_FMT(v)None)(uv()), ','.join, (lambda .0: for v in .0:
_FMT(v)None)(vv())))
def _plane(b, cache, center, normal, refdir):
    '''平面：AXIS2_PLACEMENT_3D(location, axis=z 法向, refdir=x)。'''
    n = (normal[0], normal[1], normal[2])
    r = (refdir[0], refdir[1], refdir[2])
    d = r[0] * n[0] + r[1] * n[1] + r[2] * n[2]
    r = (r[0] - d * n[0], r[1] - d * n[1], r[2] - d * n[2])
    rl = math.sqrt(r[0] ** 2 + r[1] ** 2 + r[2] ** 2)
    if rl < 1e-12:
        raise ValueError('封盖参考方向与法向平行，无法建面')
    r = (r[0] / rl, r[1] / rl, r[2] / rl)
    d_o = _pt(b, cache, center)
    d_z = "'',(%s,%s,%s)"(None, tuple % (lambda .0: for c in .0:
_FMT(c)None)(n()))
    d_x = "'',(%s,%s,%s)"(None, tuple % (lambda .0: for c in .0:
_FMT(c)None)(r()))
    pl = b.add('AXIS2_PLACEMENT_3D', "'',#%d,#%d,#%d" % (d_o, d_z, d_x))
    return b.add('PLANE', "'',#%d" % pl)
def _wrap_data_lines(lines, limit = (250,)):
    pass


def _ctrl_bbox(pieces):
    '''控制点网的包围盒（不是曲面真实包围盒）。

    为什么要算它：NX2007 实测 AskBoundingBox 对 B 样条体返回的就是**控制点网的
    包围盒**（每侧再加 0.0005 余量）。默认算例对账：
        控制网 X [-17.374426, 17.374426]  Z [-0.055813, 75.055813]
        NX 报    [-17.374926, 17.374926]     [-0.056313, 75.056313]
    而真实外形只有 ±16.875、Z 0→75 —— 差出来的那 0.5 mm 是**几何固有**的：
    螺旋中心线本身是弯的，控制点必然被推离曲线（往曲率反向），偏移量随段距 h² 走，
    seg=16 时约 0.22×线半径。这不是 bug，把段数加密会变小，但不会消失。
    后果只有一个：在 CAD 里读「包围盒」会偏大，量尺寸要直接量曲面。
    '''
    lo = [
        1e+30,
        1e+30,
        1e+30]
    hi = [
        -1e+30,
        -1e+30,
        -1e+30]
    for q in pieces:
        for row in q['P']:
            for pnt in row:
                for k in range(3):
                    if pnt[k] < lo[k]:
                        lo[k] = pnt[k]
                    if pnt[k] > hi[k]:
                        hi[k] = pnt[k]
                    return (tuple(lo), tuple(hi))
def write_step_smooth(path, S, name, simple_units):
    '''把 build_tube_surface 的结果写成光滑 STEP 实体。'''
    name = _ASCII(name)
    b = spring3d._StepBuilder()
    cache = { }
    pieces = S['pieces']
    seam_edge = { }
    rim_edge = { }
    vert = { }

    def vertex(pt):
        k = (lambda .0: for c in .0:
    _FMT(c)None)(pt())
        if k not in vert:
            vert[k] = b.add('VERTEX_POINT', "'',#%d" % _pt(b, cache, pt))
        return vert[k]
    for qi, q in enumerate(pieces):
        (P, U, V, nu, nv) = (q['P'], q['U'], q['V'], q['nu'], q['nv'])
        seam = range(nu + 1)()
        cid = _bspline_curve(b, cache, seam, U, SN.DEG)
        v0 = vertex(seam[0])
        v1 = vertex(seam[-1])
        seam_edge[qi] = b.add('EDGE_CURVE', "'',#%d,#%d,#%d,.T." % (v0, v1, cid))
        for ri, ring in enumerate(S['rings']):
            cid = _bspline_curve(b, cache, ring, pieces[0]['V'], SN.DEG)
            vv = vertex(ring[0])
            rim_edge[ri] = b.add('EDGE_CURVE', "'',#%d,#%d,#%d,.T." % (vv, vv, cid))

            def oe(eid, sense):
                return b.add('ORIENTED_EDGE', "'',*,*,#%d,%s" % (eid, '.T.' if sense else '.F.'))
            face_ids = []
            for qi, q in enumerate(pieces):
                surf = _bspline_surface(b, cache, q['P'], q['U'], q['V'])
                loop = 'EDGE_LOOP'("'',(%s)", ','.join % (lambda .0: for x in .0:
'#%d' % xNone)((oe(seam_edge[qi], True), oe(rim_edge[qi + 1], True), oe(seam_edge[qi], False), oe(rim_edge[qi], False))()))
                bound = b.add('FACE_OUTER_BOUND', "'',#%d,.T." % loop)
                face_ids.append(b.add('ADVANCED_FACE', "'',(#%d),#%d,.T." % (bound, surf)))
                for cap, ring_i, sense in ((S['cap0'], 0, True), (S['cap1'], len(pieces), False)):
                    nrm = cap['normal']
                    C = cap['center']
                    ry = -C[1]
                    rx = -C[0]
                    rl = math.sqrt(rx * rx + ry * ry)
                    ref = (rx / rl, ry / rl, 0) if rl > 1e-12 else (1, 0, 0)
                    pl = _plane(b, cache, C, nrm, ref)
                    loop = b.add('EDGE_LOOP', "'',(#%d)" % oe(rim_edge[ring_i], sense))
                    bound = b.add('FACE_OUTER_BOUND', "'',#%d,.T." % loop)
                    face_ids.append(b.add('ADVANCED_FACE', "'',(#%d),#%d,.T." % (bound, pl)))
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
    refs = (lambda .0: for i in .0:
f'''#{i}'''None)(face_ids())
    shell = b.add_multi([
        f'''CLOSED_SHELL(\'{name}\',(\n''',
        refs + '\n',
        '))'])
    solid = b.add('MANIFOLD_SOLID_BREP', f'''\'{name}\',#{shell}''')
    absr = b.add('ADVANCED_BREP_SHAPE_REPRESENTATION', f'''\'\',(#{solid}),#{grc}''')
    b.add('SHAPE_DEFINITION_REPRESENTATION', f'''#{pds},#{absr}''')
    f = open(path, 'w', encoding = 'utf-8', newline = '\n')
    f.write('ISO-10303-21;\n')
    f.write('HEADER;\n')
    f.write("FILE_DESCRIPTION(('SpringTool smooth compression spring'),'2;1');\n")
    ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    f.write(f'''FILE_NAME(\'{_ASCII(os.path.basename(path))}\',\'{ts}\',(\'\'),(\'\'),\'SpringTool\',\'SpringTool\',\'\');\n''')
    f.write("FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));\n")
    f.write('ENDSEC;\n')
    f.write('DATA;\n')
    for ln in _wrap_data_lines(b.lines):
        f.write(ln + '\n')
        f.write('ENDSEC;\nEND-ISO-10303-21;\n')
        ','.join(None, None)
    with None:
        if not None:
            pass
    return {
        'faces': len(face_ids),
        'file_size': os.path.getsize(path),
        'bbox_ctrl': _ctrl_bbox(pieces) }
def export_smooth(path, d, D, n, H0, nt, seg_per_turn, n_phi, simple_units):
    '''一步到位：建曲面 -> 写光滑 STEP。'''
    S = SN.build_tube_surface(d, D, n, H0, nt = nt, seg_per_turn = seg_per_turn, n_phi = n_phi)
    st = write_step_smooth(path, S, simple_units = simple_units)
    st['n_ctrl'] = S['n_ctrl']
    return st

