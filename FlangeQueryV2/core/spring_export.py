# -*- coding: utf-8 -*-
"""压缩弹簧三维导出：STL 三角网格 + CadQuery STEP。"""

import json
import math
import os
import struct
import subprocess
import tempfile

SEG_WIRE = 16
PTS_PER_TURN = 48


def _pitch_and_bounds(d, H0, n, nt):
    if nt < n:
        raise ValueError('总圈数小于有效圈数')
    p = (H0 - d - d * (nt - n)) / n
    if p < d:
        raise ValueError('自由高度低于压并高度，无法生成三维模型')
    return p, (nt - n) / 2.0


def _centerline_z(theta, d, H0, n, nt, p, nd):
    per = 2.0 * math.pi
    t_dead = per * nd
    t_act = per * n
    if theta <= t_dead:
        return d / 2.0 + d * theta / per
    if theta <= t_dead + t_act:
        return d / 2.0 + d * nd + p * (theta - t_dead) / per
    return d / 2.0 + d * nd + p * n + d * (theta - t_dead - t_act) / per


def _centerline_dz(theta, d, n, nt, p, nd):
    per = 2.0 * math.pi
    t_dead = per * nd
    t_act = per * n
    if theta <= t_dead or theta > t_dead + t_act:
        return d / per
    return p / per


def build_compression_mesh(d, D, n, H0, nt=None, seg=SEG_WIRE,
                           ppt=PTS_PER_TURN):
    """返回 (verts, faces)：圆截面钢丝沿变节距螺旋线的闭合网格。"""
    if nt is None:
        nt = n + 2.0
    if d <= 0 or D <= 0 or n <= 0 or H0 <= 0:
        raise ValueError('d/D/n/H0 必须为正数')
    pitch, nd = _pitch_and_bounds(d, H0, n, nt)
    R = D / 2.0
    r = d / 2.0
    per = 2.0 * math.pi
    n_ring = max(int(round(ppt * nt)), 8)
    verts, ring_start = [], []
    for i in range(n_ring + 1):
        theta = per * nt * i / n_ring
        cx, cy = R * math.cos(theta), R * math.sin(theta)
        cz = _centerline_z(theta, d, H0, n, nt, pitch, nd)
        dz = _centerline_dz(theta, d, n, nt, pitch, nd)
        tx, ty, tz = -R * math.sin(theta), R * math.cos(theta), dz
        tn = math.sqrt(tx * tx + ty * ty + tz * tz)
        tx, ty, tz = tx / tn, ty / tn, tz / tn
        ux, uy = -math.cos(theta), -math.sin(theta)
        dot = ux * tx + uy * ty
        ex, ey, ez = ux - dot * tx, uy - dot * ty, -dot * tz
        en = math.sqrt(ex * ex + ey * ey + ez * ez)
        ex, ey, ez = ex / en, ey / en, ez / en
        bx = ty * ez - tz * ey
        by = tz * ex - tx * ez
        bz = tx * ey - ty * ex
        ring_start.append(len(verts))
        for j in range(seg):
            phi = per * j / seg
            c, s = math.cos(phi) * r, math.sin(phi) * r
            verts.append((cx + c * ex + s * bx,
                          cy + c * ey + s * by,
                          cz + c * ez + s * bz))
    faces = []
    for i in range(n_ring):
        a0, b0 = ring_start[i], ring_start[i + 1]
        for j in range(seg):
            j2 = (j + 1) % seg
            v00, v01 = a0 + j, a0 + j2
            v10, v11 = b0 + j, b0 + j2
            faces.append((v00, v10, v11))
            faces.append((v00, v11, v01))
    for ring, is_top in ((0, False), (n_ring, True)):
        theta = per * nt if is_top else 0.0
        cz = _centerline_z(theta, d, H0, n, nt, pitch, nd)
        c_idx = len(verts)
        verts.append((R * math.cos(theta), R * math.sin(theta), cz))
        base = ring_start[ring]
        for j in range(seg):
            j2 = (j + 1) % seg
            if is_top:
                faces.append((c_idx, base + j2, base + j))
            else:
                faces.append((c_idx, base + j, base + j2))
    if _signed_volume(verts, faces) < 0:
        faces = [(a, c, b) for a, b, c in faces]
    return verts, faces


def _signed_volume(verts, faces):
    v6 = 0.0
    for a, b, c in faces:
        ax, ay, az = verts[a]
        bx, by, bz = verts[b]
        cx, cy, cz = verts[c]
        v6 += ax * (by * cz - bz * cy) + ay * (bz * cx - bx * cz) \
            + az * (bx * cy - by * cx)
    return v6 / 6.0


def mesh_stats(verts, faces):
    edges = {}
    for a, b, c in faces:
        for u, v in ((a, b), (b, c), (c, a)):
            key = (u, v) if u < v else (v, u)
            edges[key] = edges.get(key, 0) + 1
    bad = sum(1 for count in edges.values() if count != 2)
    xs = [v[0] for v in verts]
    ys = [v[1] for v in verts]
    zs = [v[2] for v in verts]
    return {'manifold': bad == 0, 'bad_edges': bad,
            'vertices': len(verts), 'faces': len(faces),
            'volume': _signed_volume(verts, faces),
            'bbox': (min(xs), min(ys), min(zs),
                     max(xs), max(ys), max(zs))}


def write_stl(path, verts, faces, header=b'FlangeQuery spring'):
    h = header[:80].ljust(80, b'\x00')
    tris = bytearray()
    for a, b, c in faces:
        ax, ay, az = verts[a]
        bx, by, bz = verts[b]
        cx, cy, cz = verts[c]
        ux, uy, uz = bx - ax, by - ay, bz - az
        vx, vy, vz = cx - ax, cy - ay, cz - az
        nx, ny, nz = (uy * vz - uz * vy, uz * vx - ux * vz,
                      ux * vy - uy * vx)
        nl = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
        tris += struct.pack('<3f', nx / nl, ny / nl, nz / nl)
        tris += struct.pack('<3f', ax, ay, az)
        tris += struct.pack('<3f', bx, by, bz)
        tris += struct.pack('<3f', cx, cy, cz)
        tris += struct.pack('<H', 0)
    with open(path, 'wb') as fh:
        fh.write(h)
        fh.write(struct.pack('<I', len(faces)))
        fh.write(tris)
    return path


_STEP_WORKER = r'''# -*- coding: utf-8 -*-
import json, os, sys
import cadquery as cq

def main():
    job = json.loads(sys.argv[1])
    p = job["params"]
    d = float(p["d"]); D = float(p["D"]); n = float(p["n"])
    H0 = float(p["H0"]); nt = float(p.get("nt") or (n + 2))
    R = D / 2.0
    pitch = (H0 - d - d * (nt - n)) / n
    pitch = max(d, pitch)
    height = pitch * nt
    helix = cq.Wire.makeHelix(pitch, height, R)
    plane = cq.Plane(origin=(R, 0, d / 2.0), normal=(0, 1, 0))
    profile = cq.Workplane(plane).circle(d / 2.0)
    solid = profile.sweep(cq.Workplane().add(helix), isFrenet=True)
    cq.exporters.export(solid, job["path"])
    if not os.path.exists(job["path"]):
        raise RuntimeError("STEP 未生成")
    print(json.dumps({"ok": True, "size": os.path.getsize(job["path"])}))
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''


def _clean_env():
    env = dict(os.environ)
    for key in ('PYTHONPATH', 'PYTHONHOME', 'QT_PLUGIN_PATH',
                'QT_QPA_PLATFORM'):
        env.pop(key, None)
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONNOUSERSITE'] = '1'
    return env


def write_step(r, path):
    """用 CadQuery/OCP 生成压缩弹簧 STEP。"""
    from core.gear_stp import find_python
    python = find_python(False)
    if not python:
        raise RuntimeError('未找到 CadQuery/OCP 环境，无法生成 STEP')
    folder = tempfile.mkdtemp(prefix='flange_spring_')
    worker = os.path.join(folder, 'spring_worker.py')
    with open(worker, 'w', encoding='utf-8') as fh:
        fh.write(_STEP_WORKER)
    payload = json.dumps({
        'params': {'d': r['d'], 'D': r['D'], 'n': r['n'],
                   'H0': r['H0'], 'nt': r.get('n1', r['n'] + 2)},
        'path': path}, ensure_ascii=False)
    result = subprocess.run(
        [python, worker, payload], capture_output=True, text=True,
        encoding='utf-8', errors='replace', timeout=300, env=_clean_env())
    if result.returncode != 0 or not os.path.exists(path):
        detail = (result.stderr or result.stdout or '').strip()[-500:]
        raise RuntimeError('STEP 生成失败：%s' % (detail or '无输出'))
    return path


def export_compression(r, path):
    """导出压缩弹簧：.stl 用内置网格，.step/.stp 用 CadQuery。"""
    if r.get('type') != 'compression':
        raise ValueError('三维导出目前仅支持压缩弹簧')
    ext = os.path.splitext(path)[1].lower()
    if ext == '.stl':
        verts, faces = build_compression_mesh(
            r['d'], r['D'], r['n'], r['H0'], r.get('n1'))
        return write_stl(path, verts, faces)
    if ext in ('.step', '.stp'):
        return write_step(r, path)
    raise ValueError('仅支持 .stl / .step / .stp')
